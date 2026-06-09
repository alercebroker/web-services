{{/*
Canonical name of the API. Defaults to the release name if appName is not set.
This is used as the name of the Deployment, Service, Ingress, HPA and as the
`app`/`name`/`service` label values, matching the original manifests.
*/}}
{{- define "ws-api.name" -}}
{{- .Values.appName | default .Release.Name -}}
{{- end -}}

{{/*
Name of the nginx sidecar ConfigMap.
*/}}
{{- define "ws-api.nginxConfigMapName" -}}
{{- printf "%s-nginx-conf" (include "ws-api.name" .) -}}
{{- end -}}
