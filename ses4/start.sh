#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

echo "Starting observability backend (Collector, Prometheus, Tempo, Grafana)..."
docker compose up -d

echo "Waiting for the OpenTelemetry Collector to accept connections..."
for _ in $(seq 1 20); do
    if (exec 3<>"/dev/tcp/localhost/4317") 2>/dev/null; then
        exec 3>&-
        break
    fi
    sleep 1
done

export OTEL_EXPORTER_OTLP_ENDPOINT="${OTEL_EXPORTER_OTLP_ENDPOINT:-http://localhost:4317}"
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-sip-calculator}"

echo "Starting the SIP Calculator with OpenTelemetry instrumentation..."
streamlit run app.py
