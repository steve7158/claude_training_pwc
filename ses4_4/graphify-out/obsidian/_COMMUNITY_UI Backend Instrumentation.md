---
type: community
cohesion: 0.10
members: 29
---

# UI Backend Instrumentation

**Cohesion:** 0.10 - loosely connected
**Members:** 29 nodes

## Members
- [[dot-__enter__()]] - code - ui/otel_setup.py
- [[dot-__exit__()]] - code - ui/otel_setup.py
- [[dot-_send_json()]] - code - ui/server.py
- [[dot-add()]] - code - ui/otel_setup.py
- [[dot-do_GET()]] - code - ui/server.py
- [[dot-do_POST()]] - code - ui/server.py
- [[dot-log_message()]] - code - ui/server.py
- [[dot-record()]] - code - ui/otel_setup.py
- [[dot-set_attribute()]] - code - ui/otel_setup.py
- [[dot-start_as_current_span()]] - code - ui/otel_setup.py
- [[BaseHTTPRequestHandler]] - code
- [[Handler]] - code - ui/server.py
- [[Optional OpenTelemetry instrumentation for the Helios evidence-review UI…]] - rationale - ui/otel_setup.py
- [[Stdlib-only web UI backend for the Helios evidence-review pipeline. Serves the…]] - rationale - ui/server.py
- [[_NoopCounter]] - code - ui/otel_setup.py
- [[_NoopHistogram]] - code - ui/otel_setup.py
- [[_NoopSpan]] - code - ui/otel_setup.py
- [[_NoopTracer]] - code - ui/otel_setup.py
- [[_invoke_pipeline()]] - code - ui/server.py
- [[get_tracer()]] - code - ui/otel_setup.py
- [[http_server]] - concept
- [[init_telemetry()]] - code - ui/otel_setup.py
- [[main()]] - code - ui/server.py
- [[otel_setup.py]] - code - ui/otel_setup.py
- [[record_pipeline_result()]] - code - ui/otel_setup.py
- [[run_pipeline()]] - code - ui/server.py
- [[server.py]] - code - ui/server.py
- [[subprocess]] - concept
- [[time]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/UI_Backend_Instrumentation
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Retrieval Allowlist Hook]]

## Top bridge nodes
- [[server.py]] - degree 12, connects to 1 community
- [[otel_setup.py]] - degree 10, connects to 1 community