{{- define "market-data-service.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "market-data-service.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "market-data-service.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "market-data-service.labels" -}}
helm.sh/chart: {{ include "market-data-service.chart" . }}
app.kubernetes.io/name: {{ include "market-data-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}} 