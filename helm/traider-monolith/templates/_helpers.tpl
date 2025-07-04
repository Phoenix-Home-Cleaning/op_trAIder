{{- define "traider-monolith.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "traider-monolith.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "traider-monolith.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "traider-monolith.labels" -}}
helm.sh/chart: {{ include "traider-monolith.chart" . }}
app.kubernetes.io/name: {{ include "traider-monolith.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}} 