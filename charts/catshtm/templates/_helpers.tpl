{{/*
Chart name (overridable via nameOverride).
*/}}
{{- define "catshtm-api.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Fully qualified app name.
Kept equal to the chart/name (no release prefix) to match the deployed resources.
*/}}
{{- define "catshtm-api.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}

{{/*
Chart label "name-version".
*/}}
{{- define "catshtm-api.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels.
*/}}
{{- define "catshtm-api.labels" -}}
helm.sh/chart: {{ include "catshtm-api.chart" . }}
{{ include "catshtm-api.selectorLabels" . }}
app.kubernetes.io/version: {{ .Chart.Version | quote }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels.
*/}}
{{- define "catshtm-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "catshtm-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
dockerconfigjson value for the image pull secret.
*/}}
{{- define "catshtm-api.imagePullSecret" -}}
{{- with .Values.imageCredentials -}}
{{- $auth := printf "%s:%s" .username .password | b64enc -}}
{{- printf "{\"auths\":{\"%s\":{\"username\":\"%s\",\"password\":\"%s\",\"email\":\"%s\",\"auth\":\"%s\"}}}" .registry .username .password .email $auth | b64enc -}}
{{- end -}}
{{- end -}}
