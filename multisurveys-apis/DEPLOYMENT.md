# Multisurvey APIs — Build & Deploy Runbook

How the `multisurveys-apis` service is built into a container image and deployed
to the ALeRCE EKS cluster. If you only read one thing, read
[Image naming](#image-naming--read-this-first) and [Known issues](#known-issues--gotchas).

## Architecture

`multisurveys-apis` is **one codebase that serves several APIs** — lightcurve,
object, magstat, crossmatch, probability, aladin, stamp, classifier. Each runs as
its own Kubernetes deployment in its own namespace `multisurvey-api-<service>`,
but they all share **one Docker image** and **one Helm chart**
([`charts/multisurvey_api/`](../charts/multisurvey_api/)).

Request path in production:

```
AWS ALB  →  EKS  →  nginx sidecar (strips the path prefix)  →  app container (uvicorn :8000)
```

Each pod has two containers: the FastAPI app and an **nginx sidecar** whose config
comes from the chart's ConfigMap. nginx terminates the per-service path prefix:
an external request to `/<service>_api/...` is forwarded to the app as `/...`
(with `proxy_pass .../;`), and nginx sets `X-Forwarded-Prefix`.

### The `root_path` / prefix-strip gotcha (why static files 404'd)

The lightcurve app sets `root_path="/lightcurve_api"` so the OpenAPI docs and the
`servers` block resolve correctly behind the proxy. But nginx **strips**
`/lightcurve_api` before forwarding, so the app actually receives `/static/...`,
`/htmx/...`, etc.

- **Normal routes** (routers, `/docs`) match on the already-stripped path → fine.
- A Starlette **`StaticFiles` mount** resolves files against the *accumulated*
  `root_path` (`/lightcurve_api/static`), so the stripped `/static/...` that
  arrives never matches → **every asset 404s**.

Fix (in [`src/lightcurve_api/api.py`](src/lightcurve_api/api.py)): serve static
files from an explicit route that delegates to `StaticFiles.get_response`, which
matches on the post-strip path while keeping ETag/Last-Modified, conditional
304s, Range, HEAD and traversal-safe lookups. **Do not** revert it to
`app.mount("/static", ...)` while `root_path` is set.

## Image naming — READ THIS FIRST

Three different names for one image float around the repo. **Only one is real:**

| Name | Where it appears | Is it deployed? |
|---|---|---|
| `ghcr.io/alercebroker/multisurvey-api` | live deployments (`image.repository` in the SSM Helm values) | ✅ **yes — the only real one** |
| `ghcr.io/alercebroker/multisurveys-apis` | automated CI (`build_template_ms.yaml`) | ❌ wrong name, nothing pulls it |
| `ghcr.io/alercebroker/multisurvey_api` | comment in `charts/multisurvey_api/values.yaml` | ❌ not used |

The image name is the **first positional argument** to `build direct`. To build
the image production actually pulls, you **must** name it explicitly and point at
the package dir:

```
build direct multisurvey-api --package-dir multisurveys-apis
```

`build direct multisurveys-apis` (what CI runs) produces the wrong name. See
[Known issues](#known-issues--gotchas) #1.

## Versioning

- The version lives only in [`pyproject.toml`](pyproject.toml) (`[tool.poetry] version`).
  The app reads it from the installed package ([`src/core/version.py`](src/core/version.py))
  for lightcurve's OpenAPI `version=` and for the versioned static-asset paths
  (`/v/<version>/static/...`), so a bump also makes browsers fetch the new JS and CSS.
- The build tags the image `["rc", "<pyproject version>"]` (see
  `get_tags` in [`ci_new/core/utils.py`](../ci_new/core/utils.py)). `rc` is a
  moving tag; the version tag should be treated as **immutable**.
- **Per-API tuning without a release.** `MAX_CONCURRENT_REQUESTS` (default 5) and
  `QUEUE_WAIT_SECONDS` (default 2) can be set in the `environment:` block of an API's
  `config.yaml`; see [CLAUDE.md](CLAUDE.md#concurrency-handlers-are-plain-def-and-each-pod-caps-requests).
- **Always bump `pyproject.toml` before building** so you don't overwrite a tag
  that is already deployed. All 8 services share this image, so reusing a tag can
  affect any of them on their next pull.

## Build

### Manual (the reliable path today)

Prerequisites — **two different tokens**:
- `GH_TOKEN` — build-arg, used inside the Dockerfile to clone private git deps.
- `GHCR_TOKEN` — push authentication to GHCR (as user `alerceadmin`).

Run from the `ci_new/` directory (the build resolves the repo root as `cwd/..`):

```bash
cd ci_new
export GH_TOKEN=...      # private-dep clone
export GHCR_TOKEN=...    # ghcr push auth

# sanity check first — confirm it computes tags [rc, <version>] and does NOT push
poetry run python main.py build direct multisurvey-api \
  --package-dir multisurveys-apis --build-args GH_TOKEN:$GH_TOKEN --dry-run

# real build + push
poetry run python main.py build direct multisurvey-api \
  --package-dir multisurveys-apis --build-args GH_TOKEN:$GH_TOKEN
```

- `direct` **pushes immediately** unless `--dry-run` is passed.
- `--build-args` takes `NAME:VALUE` pairs (split on the first `:`).

### Automated (build only)

[`cd-multisurvey.yaml`](../.github/workflows/cd-multisurvey.yaml) fires on push to
`main`/`staging` that touches `multisurveys-apis/**`, calling
[`build_template_ms.yaml`](../.github/workflows/build_template_ms.yaml), which runs
`build direct multisurveys-apis` in `ci_new/`.

⚠️ Two caveats: it builds the **wrongly-named** `multisurveys-apis` image, and it
**does not deploy**. Treat automated CI as "build a wrong-named image"; the real
build + deploy is manual.

## Deploy

There is **no automated deploy** for multisurvey APIs — `cd-multisurvey.yaml` only
builds. Deploy by hand, **with Helm, from the values stored in AWS SSM**.

⚠️ **Don't change live deployments with `kubectl set image` / `kubectl set resources` /
`kubectl edit`.** That drifts from the values in SSM, and the next Helm upgrade
silently reverts it. Every change (image tag, memory limit, env vars, ...) goes into
the SSM parameter first, then out through `helm upgrade`.

### Where things live

- **Chart:** the local [`charts/multisurvey_api/`](../charts/multisurvey_api/). No Helm
  repo is involved.
- **Values:** one SSM parameter per API, `/multisurvey-api/<release>-helm-values`
  (production account, `us-east-1`). It holds everything: `image.tag`, `resources`,
  `configYaml` (the app's `config.yaml`, including its env vars), ingress, probes.
  Older parameters named `multisurvey-api-<release>_helm_values` (no leading `/`) are
  stale copies from 03/2026; don't use them.
- **Helm releases** are in Helm namespace **`default`**, while the pods run in
  `multisurvey-api-<service>`. Every `helm` command needs `-n default`.

| API | Helm release | SSM parameter | k8s namespace / deployment |
|---|---|---|---|
| aladin | `multisurvey-api-aladin` | `/multisurvey-api/aladin-helm-values` | `multisurvey-api-aladin` |
| classifier | `multisurvey-api-classifier` | `/multisurvey-api/classifier-helm-values` | `multisurvey-api-classifier` |
| crossmatch | `multisurvey-api-crossmatch` | `/multisurvey-api/crossmatch-helm-values` | `multisurvey-api-crossmatch` |
| lightcurve | `multisurvey-api-lightcurve` | `/multisurvey-api/lightcurve-helm-values` | `multisurvey-api-lightcurve` |
| magstat | `multisurvey-api-magstats` | `/multisurvey-api/magstats-helm-values` | `multisurvey-api-magstat` (no `s`) |
| object | `multisurvey-api-object` | `/multisurvey-api/object-helm-values` | `multisurvey-api-object` |
| probability | `multisurvey-api-probability` | `/multisurvey-api/probability-helm-values` | `multisurvey-api-probability` |
| stamp | `multisurvey-api-stamp` | `/multisurvey-api/stamp-helm-values` | `multisurvey-api-stamp` |

### Deploy: `scripts/upgrade_multisurvey_hybrid.sh`

The script follows the rules above and prints each step as it goes. Name the APIs to
deploy (there is no "all"); it handles them one at a time, in the order given, so put a
low-traffic one first (e.g. probability) and check it before it moves on:

```bash
aws sso login --profile <your production profile>
scripts/upgrade_multisurvey_hybrid.sh --profile <your production profile> probability lightcurve magstat
```

The AWS profile name is whatever you called it in `~/.aws/config`, so pass yours with
`--profile` or `AWS_PROFILE`. The kubectl context name doesn't matter either: the script
checks that your current context is EKS cluster `hybrid`, in the same account as your AWS
credentials, and stops otherwise. Needs `aws`, `kubectl`, and `helm` with the
[`helm-diff`](https://github.com/databus23/helm-diff) plugin.

For each API it:

1. reads the values from SSM into a private temp file (deleted on exit), and checks with
   `helm diff --three-way-merge` that the cluster still matches them. If not, it shows the
   drift and asks before going on;
2. sets `image.tag` (default: the version in `pyproject.toml`; `--tag` to choose another);
3. shows the `helm diff` of the change and asks for confirmation;
4. writes the values to SSM, reads them back, and runs `helm upgrade` with exactly what
   SSM holds;
5. waits for `kubectl rollout status`, prints the image digests the pods run, checks that
   Helm, SSM and the cluster agree, and prints the commands to undo it.

Options: `--dry-run` stops after the diff; `--edit` opens the values in `$EDITOR` before
the diff, for other changes (e.g. a memory limit); `--keep-tag` with `--edit` changes
values without touching the image. `--help` has the details.

The manual equivalent, for one API (`svc` is the release suffix from the table, `ns` the
namespace):

```bash
export AWS_PROFILE=<your production profile> AWS_REGION=us-east-1
svc=probability; ns=multisurvey-api-probability; param=/multisurvey-api/$svc-helm-values
umask 077; f=$(mktemp --suffix=.yaml)   # the values include sensitive data
aws ssm get-parameter --name $param --with-decryption --query Parameter.Value --output text > $f
sed -i -E '/^image:/,/^[^ ]/ s/^(  tag: ).*/\10.2.11/' $f   # or edit $f by hand
helm diff upgrade multisurvey-api-$svc charts/multisurvey_api -n default -f $f --three-way-merge
aws ssm put-parameter --name $param --value file://$f --overwrite
helm upgrade multisurvey-api-$svc charts/multisurvey_api -n default \
  -f <(aws ssm get-parameter --name $param --with-decryption --query Parameter.Value --output text)
kubectl rollout status deploy/$ns -n $ns
rm -f $f
```

**Rolling back:** `helm rollback multisurvey-api-$svc -n default` returns to the previous
Helm revision. Then put the previous values back in SSM too, so the two match again; SSM
keeps every version (`aws ssm get-parameter --name "$param:<version>"`, version numbers
from `aws ssm get-parameter-history --name $param`).

The old `ci/` Dagger deploy (`deploy <pkg> production`) does **not** fit these APIs: it
reads `<pkg>-service-helm-values` and pulls the chart from a Helm repo. `ci_new`'s deploy
is broken (see Known issues #3).

### What is running now

```bash
helm list -n default | grep multisurvey-api        # revision and date of each release

# image of each deployment
kubectl get deploy -A -o jsonpath='{range .items[*]}{.metadata.namespace}{"\t"}{.spec.template.spec.containers[*].image}{"\n"}{end}' | grep multisurvey
```

## Verify

```bash
# public (through ALB + nginx)
curl -so /dev/null -w '%{http_code}\n' https://api-lsst.alerce.online/lightcurve_api/static/lightcurve.css   # expect 200
curl -s https://api-lsst.alerce.online/lightcurve_api/openapi.json | head

# in-pod, bypassing nginx (note: app sees the STRIPPED path)
kubectl exec -n multisurvey-api-lightcurve deploy/multisurvey-api-lightcurve -c multisurvey-api -- \
  curl -so /dev/null -w '%{http_code}\n' localhost:8000/static/lightcurve.css   # expect 200 with the fix
```

## Known issues / gotchas

_As of 02/10/2026. These are documented, not yet fixed — see the table/notes if behavior surprises you._

1. **Three image names.** Automated CI builds `multisurveys-apis`; deployments pull
   `multisurvey-api`; the chart comment says `multisurvey_api`. Only `multisurvey-api`
   is real. Until unified, always build with
   `build direct multisurvey-api --package-dir multisurveys-apis`.
2. **No automated deploy.** `cd-multisurvey.yaml` only builds; deploys are manual.
3. **`ci_new` deploy is broken.** The poetry script entry is typo'd
   (`deploy = "cli.deplot:app"` in [`ci_new/pyproject.toml`](../ci_new/pyproject.toml)),
   and [`ci_new/cli/deploy.py`](../ci_new/cli/deploy.py) calls `deploy(packages, dry_run)`
   while [`ci_new/core/deploy.py`](../ci_new/core/deploy.py) expects
   `(packages, stage, dry_run)`. Use the Helm steps under [Deploy](#deploy).
4. **Chart-path filter mismatch.** `cd-multisurvey.yaml` watches `charts/multisurvey/**`
   but the chart dir is `charts/multisurvey_api/`, so chart-only edits don't trigger CI.
5. **Shared-tag risk.** All 8 services share the `multisurvey-api` image. Reusing or
   overwriting a tag can change any of them on their next pull. Bump `pyproject.toml`
   for a fresh, distinct tag every time.
6. **Pod annotations and labels are lost.** In every `/multisurvey-api/*-helm-values`
   parameter, the entries under `podAnnotations` / `podLabels` (`prometheus.io/scrape`,
   `step-name`, `survey_lsst`, `survey_ztf`) are indented with non-breaking spaces, so
   YAML reads them as top-level keys and the pods get neither. Fixing the indentation
   adds them to the pods, which changes what Prometheus scrapes; do it as its own
   change, not inside a release.
7. **The staging script is still the old kind.** `scripts/upgrade_multisurvey_staging.sh`
   upgrades all eight releases from git-ignored local values files
   (`values_<name>_staging.yaml`), not from SSM, and restarts every Deployment.

## Reference

- Build/deploy tooling: [`ci_new/`](../ci_new/) (build works, deploy broken),
  [`ci/`](../ci/) (older Dagger pipeline, deploy works — used by other services).
- Chart: [`charts/multisurvey_api/`](../charts/multisurvey_api/) —
  `templates/deployment.yaml` (app + nginx sidecar), `templates/configmap.yaml`
  (the nginx prefix-stripping config).
- App entry: [`scripts/run_api.py`](scripts/run_api.py) (sets `API_URL` from config),
  [`src/lightcurve_api/api.py`](src/lightcurve_api/api.py).
