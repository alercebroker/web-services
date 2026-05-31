#!/usr/bin/env bash
# Helm upgrade + rollout restart for all multisurvey APIs on staging.
# Must be run from the root of the web-services repository.

set -euo pipefail

CHART_DIR="./charts/multisurvey_api"
REQUIRED_CONTEXT="staging"
HELM_RELEASE_NS="default"   # where Helm stores release metadata

# --- context guard -----------------------------------------------------------
CURRENT_CONTEXT="$(kubectl config current-context)"
if [[ "${CURRENT_CONTEXT}" != "${REQUIRED_CONTEXT}" ]]; then
  echo "ERROR: current kubectl context is '${CURRENT_CONTEXT}', expected '${REQUIRED_CONTEXT}'."
  echo "       Run: kubectl config use-context ${REQUIRED_CONTEXT}"
  exit 1
fi
echo "Context OK: ${CURRENT_CONTEXT}"
echo ""

# --- release matrix: RELEASE  VALUES_FILE  RESOURCES_NS ------------------------
declare -a RELEASES=(
  "multisurvey-api-aladin      values_aladin_staging.yaml      multisurvey-api-aladin"
  "multisurvey-api-classifier  values_classifier_staging.yaml  multisurvey-api-classifier"
  "multisurvey-api-crossmatch  values_crossmatch_staging.yaml  multisurvey-api-crossmatch"
  "multisurvey-api-lightcurve  values_lightcurve_staging.yaml  multisurvey-api-lightcurve"
  "multisurvey-api-magstats    values_magstat_staging.yaml     multisurvey-api-magstat"
  "multisurvey-api-object      values_objects_staging.yaml     multisurvey-api-object"
  "multisurvey-api-probability values_probability_staging.yaml multisurvey-api-probability"
  "multisurvey-api-stamp       values_stamp_staging.yaml       multisurvey-api-stamp"
)

for entry in "${RELEASES[@]}"; do
  read -r release values_file resources_ns <<< "${entry}"

  echo "======================================================================="
  echo "Release  : ${release}"
  echo "Values   : ${CHART_DIR}/${values_file}"
  echo "Res. NS  : ${resources_ns}"
  echo "-----------------------------------------------------------------------"

  helm upgrade "${release}" "${CHART_DIR}" \
    --namespace "${HELM_RELEASE_NS}" \
    -f "${CHART_DIR}/${values_file}" \
    --atomic \
    --wait \
    --timeout 10m

  echo "Helm upgrade done. Restarting deployments in ${resources_ns} ..."
  kubectl rollout restart deployment -n "${resources_ns}"
  kubectl rollout status deployment -n "${resources_ns}" --timeout=5m
  echo ""
done

echo "======================================================================="
echo "All multisurvey staging upgrades and rollouts complete."
