# Observability: OpenTelemetry + Grafana

`ui/server.py` (the Helios evidence-review web UI backend) is optionally
instrumented with OpenTelemetry and ships traces/metrics to a local Grafana
stack (Collector -> Tempo/Prometheus -> Grafana). "Optionally" is load-
bearing: `ui/server.py` is documented in `README.md` as stdlib-only, so
`ui/otel_setup.py` degrades to no-op stubs when `opentelemetry-*` isn't
installed — the server runs identically either way, it just doesn't emit
telemetry.

## What's captured

`ui/server.py` has one meaningful unit of work per request: shelling out to
`claude -p` to run the full governed evidence-review pipeline. So instead of
HTTP-framework/DB auto-instrumentation (there's no framework or database
here — it's a stdlib `BaseHTTPRequestHandler`), this setup captures:

- A manual span `helios.run_pipeline` around each `/api/ask` request,
  tagged with `helios.pipeline.status` (the fixed schema's `status` field:
  `answered` / `insufficient_evidence` / `escalated`, or `error` if the CLI
  call itself failed).
- A counter `helios.pipeline.requests_total` (by `status`) and a histogram
  `helios.pipeline.duration_ms`, both tagged by `status`.

This intentionally does **not** trace inside the pipeline itself (each
subagent runs in the separate `claude` CLI subprocess's own context — there
is no in-process call graph to instrument there). It traces the boundary
this project actually owns: the UI backend's request lifecycle.

## Files

- `ui/otel_setup.py` — configures the global `TracerProvider`/`MeterProvider`
  (or no-op stubs if OTel isn't installed) and exports over OTLP.
- `requirements-observability.txt` — the OTel packages, kept separate from
  the project's stdlib-only default so installing them is opt-in.
- `otel-collector-config.yaml` — Collector config (OTLP receiver, batch
  processor, exports to Tempo + Prometheus).
- `docker-compose.yaml` — Collector, Tempo, Prometheus, Grafana containers.
- `prometheus.yml` — Prometheus scrape config (scrapes the Collector's
  Prometheus exporter on `:8889`).
- `tempo.yaml` — Tempo config (local storage backend).
- `grafana/provisioning/datasources/datasources.yaml` — auto-provisions
  Prometheus and Tempo as Grafana data sources.
- `start.sh` — brings up the Docker Compose backend, waits for the
  Collector, then runs `ui/server.py` with OTel env vars set.

## Running it

```bash
pip install -r requirements-observability.txt
./start.sh
```

This starts the Docker Compose backend, waits for the Collector's OTLP port,
then runs `python3 ui/server.py` with `OTEL_EXPORTER_OTLP_ENDPOINT` and
`OTEL_SERVICE_NAME` set. Open `http://127.0.0.1:8787`, submit a research
question, and each request emits a trace and updates the metrics.

## Verifying in Grafana

1. Open `http://localhost:3000` and log in with `admin` / `admin` (set in
   `docker-compose.yaml`; change it before using this anywhere but local
   dev).
2. **Prometheus** and **Tempo** are already provisioned as data sources
   (Connections -> Data sources).
3. Check metrics: Explore -> select **Prometheus** -> query
   `helios_pipeline_requests_total` or `helios_pipeline_duration_ms_bucket`.
   Values appear/increase after asking a question through the UI.
4. Check traces: Explore -> select **Tempo** -> "Search" -> filter by
   `service.name = helios-evidence-review`. Each request produces a
   `helios.run_pipeline` span tagged with its outcome status.
5. If nothing shows up: confirm `docker compose ps` shows all four
   containers running, that `pip install -r requirements-observability.txt`
   actually ran in the environment `ui/server.py` is using, and that the
   server process printed no OTLP export errors on stderr.

See `README.md` for the load-testing setup (`k6/load-test.js`,
`docker-compose.k6.yaml`) that exercises this same pipeline under load.
