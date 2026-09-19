# Observability: OpenTelemetry + Grafana

This app is instrumented with OpenTelemetry and ships traces/metrics to a
local Grafana stack (Collector -> Tempo/Prometheus -> Grafana).

Note on scope: the SIP Calculator is a single-process Streamlit app with no
HTTP route handlers or database calls (Streamlit manages its own request
lifecycle internally). So instead of HTTP/DB auto-instrumentation, this setup
captures:
- System metrics (CPU, memory, network) via `SystemMetricsInstrumentor`.
- Manual spans around the app's actual work: `compute_sip_schedule`,
  `render_growth_chart`, `render_breakdown_chart`.
- A counter (`sip.schedule.computations`) and histogram
  (`sip.schedule.duration_ms`) for each schedule computation.

## Files

- `otel_setup.py` — configures the global `TracerProvider`/`MeterProvider` and exports over OTLP.
- `otel-collector-config.yaml` — Collector config (OTLP receiver, batch processor, exports to Tempo + Prometheus).
- `docker-compose.yaml` — Collector, Tempo, Prometheus, Grafana containers.
- `prometheus.yml` — Prometheus scrape config (scrapes the Collector's Prometheus exporter on `:8889`).
- `tempo.yaml` — Tempo config (local storage backend).
- `grafana/provisioning/datasources/datasources.yaml` — auto-provisions Prometheus and Tempo as Grafana data sources.
- `start.sh` — brings up the backend, then runs the app with OTel env vars set.

## Running it

```bash
pip install -r requirements.txt
./start.sh
```

This starts the Docker Compose backend, waits for the Collector's OTLP port,
then runs `streamlit run app.py` with `OTEL_EXPORTER_OTLP_ENDPOINT` and
`OTEL_SERVICE_NAME` set. Open the app (usually `http://localhost:8501`) and
interact with the sliders — each rerun emits a trace and updates the metrics.

## Verifying in Grafana

1. Open `http://localhost:3000` and log in with `admin` / `admin` (set in `docker-compose.yaml`; change it before using this anywhere but local dev).
2. **Prometheus** and **Tempo** are already provisioned as data sources (Connections -> Data sources).
3. Check metrics: Explore -> select **Prometheus** -> query `sip_schedule_computations_total` or `sip_schedule_duration_ms_bucket`. You should see values appear/increase after using the app. System metrics appear as `system_cpu_utilization_ratio`, `system_memory_usage_bytes`, etc.
4. Check traces: Explore -> select **Tempo** -> "Search" -> filter by `service.name = sip-calculator`. Each app interaction should produce a trace with `compute_sip_schedule`, `render_growth_chart`, and `render_breakdown_chart` spans.
5. If nothing shows up: confirm `docker compose ps` shows all four containers running, and that the Streamlit process printed no OTLP export errors in its terminal.
