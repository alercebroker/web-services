#!/usr/bin/env bash
# Deploy multisurvey APIs to production (EKS cluster "hybrid") with Helm, from the values in AWS SSM.
#
# The rules this script follows (see multisurveys-apis/DEPLOYMENT.md):
#   - Each API's Helm values live in the SSM parameter /multisurvey-api/<release>-helm-values. They are the
#     record of what runs in production.
#   - Every change goes into SSM first, then out through `helm upgrade` with the values read back from SSM.
#   - Never `kubectl set image` / `set resources` / `edit` a live Deployment: it drifts from SSM, and the next
#     `helm upgrade` silently reverts it.
#   - One API at a time, each change reviewed with `helm diff` before it is applied.
#
# Run with --help for usage.

set -euo pipefail

# --- constants (real AWS and k8s names, not local aliases) ---------------------------------------------------
EKS_CLUSTER="hybrid"   # the EKS cluster's name in AWS
AWS_REGION_PROD="us-east-1"   # where the cluster and the SSM parameters live; set on every aws call, because a
                              # developer's profile may default to another region
HELM_RELEASE_NS="default"   # Helm keeps the release records here; the pods run in multisurvey-api-<api>
CHART_DIR="charts/multisurvey_api"
IMAGE_REPO="ghcr.io/alercebroker/multisurvey-api"
API_NAMES="aladin classifier crossmatch lightcurve magstat object probability stamp"

usage() {
  cat <<EOF
Usage: scripts/upgrade_multisurvey_hybrid.sh [options] <api> [<api> ...]

Deploys the named multisurvey APIs to production, one at a time. For each API it reads the Helm values
from AWS SSM, sets the image tag, shows a helm diff, asks for confirmation, writes the values back to SSM,
runs helm upgrade with what SSM now holds, and waits for the rollout.

  <api>         one or more of: ${API_NAMES}
                There is no "all": name each API you mean to deploy.

Options:
  --tag TAG     image tag to deploy (default: the version in multisurveys-apis/pyproject.toml)
  --keep-tag    don't change the image tag (with --edit, for a values-only change such as a memory limit)
  --edit        open the values in \$EDITOR before the diff, to make other changes
  --profile P   AWS CLI profile to use. Profile names are local (whatever you called it in ~/.aws/config),
                so pass yours, or set AWS_PROFILE. Without either, the AWS CLI's default credentials are used.
  --dry-run     stop after showing the diff; nothing is changed
  -h, --help    show this help

The cluster is the one in your current kubectl context. The script checks that it is EKS cluster
"${EKS_CLUSTER}" in the same AWS account as your credentials, whatever your context is called.
EOF
}

# --- output helpers ---------------------------------------------------------------------------------------------
bold=$'\e[1m'; red=$'\e[31m'; yellow=$'\e[33m'; green=$'\e[32m'; reset=$'\e[0m'
[[ -t 1 ]] || { bold=""; red=""; yellow=""; green=""; reset=""; }
step() { echo; echo "${bold}==> $*${reset}"; }
info() { echo "    $*"; }
warn() { echo "${yellow}    WARNING: $*${reset}"; }
die() { echo "${red}ERROR: $*${reset}" >&2; exit 1; }
confirm() {  # confirm "question" -> returns 0 on y/yes; no terminal counts as "no"
  local answer=""
  if ! { true </dev/tty; } 2>/dev/null; then
    echo "    $1 -> no terminal to ask on, so: no"; return 1
  fi
  read -r -p "${bold}    $1 [y/N] ${reset}" answer </dev/tty || return 1
  [[ "${answer}" =~ ^[Yy]([Ee][Ss])?$ ]]
}

# --- arguments --------------------------------------------------------------------------------------------------
tag=""; keep_tag=false; edit=false; dry_run=false; apis=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --tag) tag="${2:?--tag needs a value}"; shift 2 ;;
    --keep-tag) keep_tag=true; shift ;;
    --edit) edit=true; shift ;;
    --profile) export AWS_PROFILE="${2:?--profile needs a value}"; shift 2 ;;
    --dry-run) dry_run=true; shift ;;
    -h|--help) usage; exit 0 ;;
    -*) die "unknown option $1 (see --help)" ;;
    *) apis+=("$1"); shift ;;
  esac
done
[[ ${#apis[@]} -gt 0 ]] || { usage; exit 1; }
for api in "${apis[@]}"; do
  [[ " ${API_NAMES} magstats " == *" ${api} "* ]] || die "unknown API '${api}'. Valid: ${API_NAMES}"
done
if ${keep_tag} && [[ -n "${tag}" ]]; then die "--tag and --keep-tag don't go together"; fi

cd "$(dirname "$0")/.."   # the repo root, so the chart and pyproject paths resolve from anywhere

# api name -> Helm release suffix, SSM parameter suffix and k8s namespace. Only magstat differs: its release and
# parameter are "magstats", its namespace "multisurvey-api-magstat".
release_of() { [[ "$1" == magstat* ]] && echo "magstats" || echo "$1"; }
namespace_of() { [[ "$1" == magstat* ]] && echo "magstat" || echo "$1"; }

# helm diff of a values file against what runs. Sets diff_rc (0 = no change, 2 = changes, else an error) and
# writes the diff, with 3 lines of context, to diff_out. --three-way-merge also catches changes made in the
# cluster outside Helm.
run_diff() {  # run_diff <release> <values file>
  diff_rc=0
  helm diff upgrade "$1" "${CHART_DIR}" -n "${HELM_RELEASE_NS}" -f "$2" \
    --three-way-merge --detailed-exitcode --context 3 >"${diff_out}" 2>&1 || diff_rc=$?
  # --detailed-exitcode reports "changes found" as errors; drop those lines, they are not failures
  if [[ ${diff_rc} -eq 2 ]]; then
    grep -v -E '^Error: (identified at least one change|plugin "diff" exited with error)' "${diff_out}" \
      >"${diff_out}.tmp" || true
    mv "${diff_out}.tmp" "${diff_out}"
  fi
}

# Prints image.tag from a values file, or nothing.
image_tag_of() {
  awk '/^image:/ {in_image=1; next} /^[^ ]/ {in_image=0} in_image && /^  tag:/ {gsub(/["'"'"']/, "", $2); print $2}' "$1"
}

# --- preflight --------------------------------------------------------------------------------------------------
step "Checking the tools"
for tool in aws helm kubectl awk sed cmp; do
  command -v "${tool}" >/dev/null || die "'${tool}' is not installed"
done
helm diff version >/dev/null 2>&1 \
  || die "the helm-diff plugin is missing: helm plugin install https://github.com/databus23/helm-diff"
info "aws, helm (with helm-diff) and kubectl found"

step "Checking your AWS credentials"
if [[ -n "${AWS_PROFILE:-}" ]]; then
  info "AWS profile: ${AWS_PROFILE}"
else
  info "AWS profile: not set, so the AWS CLI uses its default credentials"
fi
identity=$(aws sts get-caller-identity --region "${AWS_REGION_PROD}" --query Arn --output text 2>&1) \
  || die "the AWS CLI has no valid credentials (${identity}).
       Log in with: aws sso login --profile <your production profile>
       then rerun with --profile <it>, or export AWS_PROFILE=<it>."
info "Authenticated as ${identity}"

step "Checking that kubectl and your AWS credentials point at the production cluster \"${EKS_CLUSTER}\""
context=$(kubectl config current-context 2>/dev/null) || die "kubectl has no current context"
context_server=$(kubectl config view --minify -o jsonpath='{.clusters[0].cluster.server}')
eks_server=$(aws eks describe-cluster --name "${EKS_CLUSTER}" --region "${AWS_REGION_PROD}" \
  --query cluster.endpoint --output text 2>/dev/null) \
  || die "your AWS credentials can't see EKS cluster '${EKS_CLUSTER}' in ${AWS_REGION_PROD}.
       They are probably for another account (staging?). Use your production profile."
[[ "${context_server}" == "${eks_server}" ]] \
  || die "your kubectl context '${context}' is not EKS cluster '${EKS_CLUSTER}'.
       Switch to the context of that cluster (kubectl config get-contexts), or create it with:
       aws eks update-kubeconfig --name ${EKS_CLUSTER} --region ${AWS_REGION_PROD}"
info "kubectl context '${context}' is EKS cluster '${EKS_CLUSTER}', in the same account as your credentials"

if ! ${keep_tag}; then
  step "Choosing the image tag"
  if [[ -z "${tag}" ]]; then
    tag=$(sed -n -E 's/^version = "([^"]+)"/\1/p' multisurveys-apis/pyproject.toml | head -1)
    [[ -n "${tag}" ]] || die "couldn't read the version from multisurveys-apis/pyproject.toml; pass --tag"
    info "Tag ${tag}, from multisurveys-apis/pyproject.toml (pass --tag to choose another)"
  else
    info "Tag ${tag}, from --tag"
  fi
  if command -v docker >/dev/null && docker manifest inspect "${IMAGE_REPO}:${tag}" >/dev/null 2>&1; then
    info "${IMAGE_REPO}:${tag} exists in the registry"
  else
    warn "couldn't confirm that ${IMAGE_REPO}:${tag} exists (the registry is private: 'docker login ghcr.io'
             enables this check). If it doesn't exist, the new pods won't start and the rollout times out."
    confirm "Continue anyway?" || exit 1
  fi
fi

workdir=$(mktemp -d)   # copies of the values: they hold sensitive data, so private and deleted on exit
chmod 700 "${workdir}"
trap 'rm -rf "${workdir}"' EXIT

# --- deploy one API -----------------------------------------------------------------------------------------------
deploy_api() {
  local api="$1" rel ns release param values readback current_tag revision ssm_version rc
  rel=$(release_of "${api}"); ns="multisurvey-api-$(namespace_of "${api}")"
  release="multisurvey-api-${rel}"; param="/multisurvey-api/${rel}-helm-values"
  values="${workdir}/${rel}.yaml"; readback="${workdir}/${rel}.readback.yaml"; diff_out="${workdir}/${rel}.diff"

  echo; echo "${bold}======== ${api}: Helm release ${release}, namespace ${ns} ========${reset}"

  step "Getting the Helm values from AWS SSM Parameter Store: ${param} (${AWS_REGION_PROD})"
  aws ssm get-parameter --name "${param}" --with-decryption --region "${AWS_REGION_PROD}" \
    --query Parameter.Value --output text >"${values}" || die "couldn't read ${param}"
  ssm_version=$(aws ssm get-parameter --name "${param}" --region "${AWS_REGION_PROD}" \
    --query Parameter.Version --output text)
  current_tag=$(image_tag_of "${values}")
  info "SSM version ${ssm_version}; image.tag there is ${current_tag:-<none>}"
  revision=$(helm history "${release}" -n "${HELM_RELEASE_NS}" --max 1 2>/dev/null | awk 'NR==2 {print $1}')
  [[ -n "${revision}" ]] || die "Helm release ${release} not found in namespace ${HELM_RELEASE_NS}"
  info "Helm release ${release} is at revision ${revision}"

  step "Checking that the cluster still matches SSM (helm diff of the unchanged SSM values against what runs)"
  run_diff "${release}" "${values}"
  if [[ ${diff_rc} -eq 0 ]]; then
    info "No drift: what runs is what SSM holds"
  elif [[ ${diff_rc} -eq 2 ]]; then
    warn "the cluster differs from SSM. Someone changed it outside this procedure (kubectl, or other values),
             or the chart in this checkout differs from the one last deployed. Upgrading will replace those
             differences with what SSM holds. The differences:"
    sed 's/^/      /' "${diff_out}"
    confirm "Go on with ${api} anyway?" || { info "Skipped ${api}"; return 0; }
  else
    cat "${diff_out}"; die "helm diff failed"
  fi

  if ! ${keep_tag}; then
    step "Setting image.tag: ${current_tag:-<none>} -> ${tag}"
    # (no sed -i: its syntax differs between GNU and macOS)
    sed -E '/^image:/,/^[^ ]/ s/^(  tag: ).*/\1'"${tag}"'/' "${values}" >"${values}.new"
    mv "${values}.new" "${values}"
    [[ "$(image_tag_of "${values}")" == "${tag}" ]] \
      || die "couldn't set image.tag: the values don't have the expected 'image:' / '  tag:' layout"
  fi
  if ${edit}; then
    step "Opening the values in ${EDITOR:-vi} for your other changes"
    "${EDITOR:-vi}" "${values}"
  fi

  step "Reviewing the change (helm diff of the new values against what runs)"
  run_diff "${release}" "${values}"
  if [[ ${diff_rc} -eq 0 ]]; then
    info "Nothing to change for ${api}"; return 0
  elif [[ ${diff_rc} -ne 2 ]]; then
    cat "${diff_out}"; die "helm diff failed"
  fi
  sed 's/^/      /' "${diff_out}"
  if ${dry_run}; then
    info "--dry-run: nothing written to SSM, nothing upgraded"; return 0
  fi
  confirm "Write these values to SSM and upgrade ${release}?" || { info "Skipped ${api}"; return 0; }

  step "Writing the new values to SSM (${param})"
  aws ssm put-parameter --name "${param}" --value "file://${values}" --overwrite \
    --region "${AWS_REGION_PROD}" --query Version --output text | sed 's/^/    New SSM version: /'

  step "Reading the values back from SSM, to deploy exactly what it holds"
  aws ssm get-parameter --name "${param}" --with-decryption --region "${AWS_REGION_PROD}" \
    --query Parameter.Value --output text >"${readback}"
  cmp -s "${values}" "${readback}" || die "SSM doesn't hold what was just written; nothing was upgraded"
  info "SSM holds the reviewed values"

  step "helm upgrade ${release} ${CHART_DIR} -n ${HELM_RELEASE_NS} (values from SSM)"
  helm upgrade "${release}" "${CHART_DIR}" -n "${HELM_RELEASE_NS}" -f "${readback}" >/dev/null \
    || die "helm upgrade failed. SSM already holds the new values: restore them with the commands below.
$(rollback_help)"
  info "Helm release ${release} is now at revision $((revision + 1))"

  step "Waiting for the rollout of deploy/${ns} in namespace ${ns}"
  kubectl rollout status "deploy/${ns}" -n "${ns}" --timeout=10m \
    || die "the rollout didn't finish. To go back:
$(rollback_help)"

  step "Checking ${api}"
  info "Images the pods run:"
  kubectl get pods -n "${ns}" \
    -o jsonpath='{range .items[*]}{.status.containerStatuses[?(@.name=="multisurvey-api")].imageID}{"\n"}{end}' \
    | sort | uniq -c | sed 's/^/      /'
  run_diff "${release}" "${readback}"
  if [[ ${diff_rc} -eq 0 ]]; then
    info "${green}Helm, SSM and the cluster agree.${reset}"
  else
    warn "helm diff still shows differences between SSM and the cluster; look before going on:"
    sed 's/^/      /' "${diff_out}"
  fi
  info "To undo:"
  rollback_help
}

rollback_help() {  # uses deploy_api's locals: release, revision, param, ssm_version
  cat <<EOF
      helm rollback ${release} ${revision} -n ${HELM_RELEASE_NS}
      aws ssm get-parameter --name "${param}:${ssm_version}" --with-decryption --region ${AWS_REGION_PROD} \\
        --query Parameter.Value --output text > old.yaml   # the previous values (sensitive: delete afterwards)
      aws ssm put-parameter --name "${param}" --value file://old.yaml --overwrite --region ${AWS_REGION_PROD}
EOF
}

for api in "${apis[@]}"; do
  deploy_api "${api}"
  if [[ "${api}" != "${apis[${#apis[@]}-1]}" ]] && ! ${dry_run}; then
    confirm "Check ${api} before going on (website, logs). Continue with the next API?" || exit 0
  fi
done
echo; echo "${bold}Done.${reset}"
