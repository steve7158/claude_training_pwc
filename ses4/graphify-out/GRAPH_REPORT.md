# Graph Report - ses4  (2026-09-19)

## Corpus Check
- 18 files · ~12,632 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 1 file(s) not represented in the graph (top: (none) 1)

## Summary
- 64 nodes · 77 edges · 6 communities (5 shown, 1 thin omitted)
- Extraction: 79% EXTRACTED · 19% INFERRED · 1% AMBIGUOUS · INFERRED: 15 edges (avg confidence: 0.88)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `37c411b5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- SIP Backend & Dependencies
- SIP App Code Structure
- Graphify Skill Core & Flows
- Graphify Project Rules
- Extraction Spec & Honesty Rules
- MCP Server Configuration

## God Nodes (most connected - your core abstractions)
1. `Graphify Skill Definition` - 13 edges
2. `Observability: OpenTelemetry + Grafana` - 7 edges
3. `compute_sip_schedule()` - 5 edges
4. `render_growth_chart()` - 5 edges
5. `render_breakdown_chart()` - 4 edges
6. `main()` - 4 edges
7. `Verifying in Grafana` - 4 edges
8. `app.py (Single-File Streamlit App)` - 4 edges
9. `Graphify Codebase-Question Rules` - 4 edges
10. `Extraction Subagent Prompt Spec` - 4 edges

## Surprising Connections (you probably didn't know these)
- `Observability: OpenTelemetry + Grafana` --references--> `compute_sip_schedule()`  [INFERRED]
  OBSERVABILITY.md → app.py
- `Verifying in Grafana` --references--> `compute_sip_schedule()`  [INFERRED]
  OBSERVABILITY.md → app.py
- `Observability: OpenTelemetry + Grafana` --references--> `render_growth_chart()`  [INFERRED]
  OBSERVABILITY.md → app.py
- `Verifying in Grafana` --references--> `render_growth_chart()`  [INFERRED]
  OBSERVABILITY.md → app.py
- `Observability: OpenTelemetry + Grafana` --references--> `render_breakdown_chart()`  [INFERRED]
  OBSERVABILITY.md → app.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Skill Reference Documentation Set** — _claude_skills_graphify_skill_definition, _claude_skills_graphify_references_add_watch_add_watch_flow, _claude_skills_graphify_references_exports_extra_exports, _claude_skills_graphify_references_extraction_spec_subagent_prompt_spec, _claude_skills_graphify_references_github_and_merge_github_clone_merge_flow, _claude_skills_graphify_references_hooks_commit_hook_integration, _claude_skills_graphify_references_query_query_path_explain_flow, _claude_skills_graphify_references_transcribe_video_transcription_flow, _claude_skills_graphify_references_update_incremental_update_flow [EXTRACTED 1.00]
- **SIP Calculator Backend Flow** — _claude_agents_backend_backend_agent, _claude_agents_backend_compute_sip_schedule, _claude_agents_backend_app_py, _claude_agents_backend_fetch_mcp_tool, _claude_agents_backend_annuity_due_convention [EXTRACTED 1.00]
- **SIP Calculator App Dependencies** — requirements_streamlit_dependency, requirements_pandas_dependency, requirements_matplotlib_dependency, requirements_mcp_server_fetch_dependency, _claude_agents_backend_app_py [INFERRED 0.85]

## Communities (6 total, 1 thin omitted)

### Community 0 - "SIP Backend & Dependencies"
Cohesion: 0.20
Nodes (10): Annuity-Due Convention, app.py (Single-File Streamlit App), Backend Agent (SIP Calculator), compute_sip_schedule, fetch MCP Tool, Extra Exports and Benchmark, matplotlib>=3.9, mcp-server-fetch>=2024.11 (+2 more)

### Community 1 - "SIP App Code Structure"
Cohesion: 0.20
Nodes (14): compute_sip_schedule(), main(), SIP Calculator — Streamlit app. Computes the future value of a monthly…, render_breakdown_chart(), render_growth_chart(), DataFrame, matplotlib_pyplot, Files (+6 more)

### Community 2 - "Graphify Skill Core & Flows"
Cohesion: 0.17
Nodes (16): Graphify Skill Trigger Directive, Add URL & Watch Folder Flow, Confidence Score Rubric, Node ID Format Rule, Extraction Subagent Prompt Spec, GitHub Clone & Cross-Repo Merge Flow, Commit Hook & CLAUDE.md Integration, Query, Path & Explain Flow (+8 more)

### Community 3 - "Graphify Project Rules"
Cohesion: 0.13
Nodes (14): opentelemetry, opentelemetry_exporter_otlp_proto_grpc_metric_exporter, opentelemetry_exporter_otlp_proto_grpc_trace_exporter, opentelemetry_instrumentation_system_metrics, opentelemetry_sdk_metrics, opentelemetry_sdk_metrics_export, opentelemetry_sdk_resources, opentelemetry_sdk_trace (+6 more)

### Community 4 - "Extraction Spec & Honesty Rules"
Cohesion: 0.50
Nodes (3): OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME, start.sh script

## Ambiguous Edges - Review These
- `fetch MCP Tool` → `Extra Exports and Benchmark`  [AMBIGUOUS]
  .claude/agents/backend.md · relation: conceptually_related_to

## Knowledge Gaps
- **15 isolated node(s):** `/home/labuser/steve-proj/claude_training_pwc/ses4/.venv/bin/python`, `start.sh script`, `OTEL_EXPORTER_OTLP_ENDPOINT`, `OTEL_SERVICE_NAME`, `Files` (+10 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 35 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `fetch MCP Tool` and `Extra Exports and Benchmark`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Graphify Skill Definition` connect `Graphify Skill Core & Flows` to `SIP Backend & Dependencies`?**
  _High betweenness centrality (0.123) - this node is a cross-community bridge._
- **Why does `Extra Exports and Benchmark` connect `SIP Backend & Dependencies` to `Graphify Skill Core & Flows`?**
  _High betweenness centrality (0.074) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `Observability: OpenTelemetry + Grafana` (e.g. with `compute_sip_schedule()` and `render_breakdown_chart()`) actually correct?**
  _`Observability: OpenTelemetry + Grafana` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `compute_sip_schedule()` (e.g. with `Observability: OpenTelemetry + Grafana` and `Verifying in Grafana`) actually correct?**
  _`compute_sip_schedule()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `render_growth_chart()` (e.g. with `Observability: OpenTelemetry + Grafana` and `Verifying in Grafana`) actually correct?**
  _`render_growth_chart()` has 2 INFERRED edges - model-reasoned connections that need verification._
- **Are the 2 inferred relationships involving `render_breakdown_chart()` (e.g. with `Observability: OpenTelemetry + Grafana` and `Verifying in Grafana`) actually correct?**
  _`render_breakdown_chart()` has 2 INFERRED edges - model-reasoned connections that need verification._