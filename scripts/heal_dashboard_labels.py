#!/usr/bin/env python3
"""Repair an ALB CloudWatch dashboard after a k8s change.

Series on the hybrid_webservices_health dashboard are keyed by ALB target group
dimension, whose name is a truncated-and-hashed derivative of the k8s object
(`k8s-multisur-multisur-213937299c`). This script treats the *label* as the
stable identity and the target group dimension as a derived value, so it can:

  - label unlabelled series               (first run)
  - fix labels that drifted               (Deployment renamed / selector moved)
  - repoint dimensions whose hash changed (Ingress / TargetGroupBinding recreated)
  - repoint the LoadBalancer dimension    (ALB recreated)
  - report series whose workload is gone  (you decide whether to delete the row)

Identity chain: TargetGroup dimension <- TargetGroupBinding.spec.targetGroupARN
<- serviceRef -> Service.spec.selector -> Deployment/StatefulSet pod template.

Reads the cluster via the current kubectl context. Dry-run by default.

    ./heal_dashboard_labels.py hybrid_webservices_health           # report only
    ./heal_dashboard_labels.py hybrid_webservices_health --apply   # write it back
"""
import argparse
import json
import subprocess
import sys

REGION = "us-east-1"


def kubectl(*args):
    out = subprocess.run(["kubectl", *args, "-o", "json"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout)["items"]


def aws(*args):
    out = subprocess.run(["aws", *args, "--region", REGION, "--output", "json"],
                         capture_output=True, text=True, check=True)
    return json.loads(out.stdout) if out.stdout.strip() else None


def workload_label(ns, name):
    """Collapse the common ns == workload case to a single token."""
    return name if name == ns else f"{ns}/{name}"


def build_index():
    """label -> {'dim': 'targetgroup/<name>/<id>', 'arn': ...}, plus ambiguous labels."""
    svcs = {(s["metadata"]["namespace"], s["metadata"]["name"]): s
            for s in kubectl("get", "svc", "-A")}
    workloads = kubectl("get", "deploy,sts", "-A")

    index, ambiguous = {}, set()
    for tgb in kubectl("get", "targetgroupbindings", "-A"):
        ns = tgb["metadata"]["namespace"]
        arn = tgb["spec"]["targetGroupARN"]
        svc_name = tgb["spec"].get("serviceRef", {}).get("name")
        selector = (svcs.get((ns, svc_name)) or {}).get("spec", {}).get("selector") or {}

        owners = [w["metadata"]["name"] for w in workloads
                  if w["metadata"]["namespace"] == ns
                  and selector
                  and all(w["spec"]["template"]["metadata"].get("labels", {}).get(k) == v
                          for k, v in selector.items())]

        if len(owners) == 1:
            label = workload_label(ns, owners[0])
        elif owners:
            label = workload_label(ns, "+".join(sorted(owners)))
        else:
            label = f"{ns}/svc:{svc_name}"

        if label in index:
            # Two target groups resolving to one workload: can't heal by label alone.
            ambiguous.add(label)
        index[label] = {"dim": arn.split(":")[-1], "arn": arn}

    for label in ambiguous:
        index.pop(label, None)
    return index, ambiguous


def current_alb_dim(arn):
    """'app/<name>/<id>' for the ALB fronting a target group, or None if unattached."""
    tgs = aws("elbv2", "describe-target-groups", "--target-group-arns", arn)
    lbs = tgs["TargetGroups"][0].get("LoadBalancerArns") or []
    if not lbs:
        return None
    # ELB ARNs end in 'loadbalancer/app/<name>/<id>'; the dimension drops that prefix.
    return lbs[0].split(":")[-1].removeprefix("loadbalancer/")


def dim_slot(metric, prefix):
    """Index of the element holding a dimension value, or None if inherited via '.'."""
    return next((i for i, e in enumerate(metric)
                 if isinstance(e, str) and e.startswith(prefix)), None)


def heal(dash, index):
    by_dim = {v["dim"]: label for label, v in index.items()}
    changes, orphans = [], []
    healed_arn = None

    for widget in dash["widgets"]:
        for metric in widget.get("properties", {}).get("metrics", []):
            slot = dim_slot(metric, "targetgroup/")
            if slot is None:
                continue
            dim = metric[slot]
            opts = metric[-1] if isinstance(metric[-1], dict) else None
            label = opts.get("label") if opts else None

            if label and label in index:
                # Label is authoritative: repoint the dimension if the hash moved.
                want = index[label]["dim"]
                healed_arn = healed_arn or index[label]["arn"]
                if dim != want:
                    metric[slot] = want
                    changes.append(f"repoint  {label}: {dim} -> {want}")
            elif dim in by_dim:
                # Unlabelled, or label drifted: trust the dimension and (re)label.
                want = by_dim[dim]
                healed_arn = healed_arn or index[want]["arn"]
                if label is None:
                    if opts is None:
                        metric.append({"label": want})
                    else:
                        opts["label"] = want
                    changes.append(f"label    {want}")
                elif label != want:
                    opts["label"] = want
                    changes.append(f"relabel  {label} -> {want}")
            else:
                orphans.append(f"{label or '(unlabelled)'}  {dim}")

    if healed_arn:
        alb = current_alb_dim(healed_arn)
        for widget in dash["widgets"]:
            for metric in widget.get("properties", {}).get("metrics", []):
                slot = dim_slot(metric, "app/")
                if slot is not None and alb and metric[slot] != alb:
                    changes.append(f"repoint  ALB: {metric[slot]} -> {alb}")
                    metric[slot] = alb
    return changes, orphans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dashboard")
    ap.add_argument("--apply", action="store_true", help="write the dashboard back")
    args = ap.parse_args()

    body = subprocess.run(
        ["aws", "cloudwatch", "get-dashboard", "--dashboard-name", args.dashboard,
         "--region", REGION, "--query", "DashboardBody", "--output", "text"],
        capture_output=True, text=True, check=True).stdout
    dash = json.loads(body)

    index, ambiguous = build_index()
    changes, orphans = heal(dash, index)

    backup = f"{args.dashboard}.backup.json"
    with open(backup, "w") as f:
        f.write(body)

    for c in changes:
        print(c)
    print(f"\n{len(changes)} change(s); previous body saved to {backup}")

    if ambiguous:
        print("\nambiguous labels (>1 target group per workload, skipped):", file=sys.stderr)
        for a in sorted(ambiguous):
            print(f"  {a}", file=sys.stderr)
    if orphans:
        print("\nno workload in cluster (series left as-is, delete the row if retired):",
              file=sys.stderr)
        for o in sorted(orphans):
            print(f"  {o}", file=sys.stderr)

    if not changes:
        return
    if not args.apply:
        print("\ndry run; re-run with --apply to write it back")
        return

    aws("cloudwatch", "put-dashboard", "--dashboard-name", args.dashboard,
        "--dashboard-body", json.dumps(dash))
    print("applied")


if __name__ == "__main__":
    main()
