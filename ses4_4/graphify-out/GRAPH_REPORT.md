# Graph Report - ses4_4  (2026-09-19)

## Corpus Check
- Corpus is ~24,762 words - fits in a single context window. You may not need a graph.

## Summary
- 182 nodes · 298 edges · 13 communities (11 shown, 2 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.68)
- Token cost: 0 input · 257,181 output

## Community Hubs (Navigation)
- Governed Pipeline Core
- UI Backend Instrumentation
- Evidence MCP Server
- GLX-9081 Evidence Corpus
- Retrieval Allowlist Hook
- Observability & Load-Test Stack
- UI Rendering Logic
- Graphify Skill Docs
- UI Presentation Layer
- k6 Load Test Script
- Startup Script
- MCP Server Registration
- Helios UI Page

## God Nodes (most connected - your core abstractions)
1. `Helios Evidence-Review Agent (CLAUDE.md governance spec)` - 20 edges
2. `Helios Evidence-Review Agent README` - 15 edges
3. `KRAS G12C (Drug Target)` - 11 edges
4. `literature-agent` - 10 edges
5. `Evidence Review skill (pipeline supervisor)` - 10 edges
6. `GLX-9081 (KRAS G12C Inhibitor Compound)` - 10 edges
7. `citation-validator` - 9 edges
8. `trial-agent` - 9 edges
9. `evidence-mcp-server / evidence_mcp_server.py` - 9 edges
10. `NSCLC (Non-Small Cell Lung Cancer)` - 9 edges

## Surprising Connections (you probably didn't know these)
- `graphify Honesty Rules` --semantically_similar_to--> `citation-validator`  [INFERRED] [semantically similar]
  .claude/skills/graphify/SKILL.md → .claude/agents/citation-validator.md
- `patent-agent / patent source_type (stretch, not built)` --conceptually_related_to--> `literature-agent`  [INFERRED]
  CLAUDE.md → .claude/agents/literature-agent.md
- `graphify query/path/explain reference` --semantically_similar_to--> `query-planner`  [INFERRED] [semantically similar]
  .claude/skills/graphify/references/query.md → .claude/agents/query-planner.md
- `Context-and-memory policy (key_points-only extraction discipline)` --cites--> `Helios Evidence-Review Agent (CLAUDE.md governance spec)`  [AMBIGUOUS]
  .claude/agents/literature-agent.md → CLAUDE.md
- `p3-triage-agent` --references--> `ui/server.py (headless pipeline backend)`  [EXTRACTED]
  .claude/agents/p3-triage-agent.md → README.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Governed Evidence-Review Pipeline** — claude_skills_evidence_review_skill_evidence_review, claude_agents_query_planner_query_planner, claude_agents_literature_agent_literature_agent, claude_agents_trial_agent_trial_agent, claude_agents_evidence_synthesizer_evidence_synthesizer, claude_agents_citation_validator_citation_validator, claude_agents_confidence_scorer_confidence_scorer [EXTRACTED 1.00]
- **CLAUDE.md / Skill / Hook / Subagent Governance Split** — claude_helios_evidence_review_agent, claude_skills_evidence_review_skill_evidence_review, claude_enforce_source_allowlist_hook, claude_agents_citation_validator_citation_validator [EXTRACTED 1.00]
- **P3 Triage Governance-Compliance Check** — claude_agents_p3_triage_agent_p3_triage_agent, claude_allowlist_json, claude_skills_evidence_review_skill_evidence_review, claude_enforce_source_allowlist_hook [EXTRACTED 1.00]
- **GLX-9081 Monotherapy Efficacy Evidence Chain** — evidence_mcp_server_data_documents_lit_501_lit_501, evidence_mcp_server_data_documents_lit_502_lit_502, evidence_mcp_server_data_documents_lit_503_lit_503, evidence_mcp_server_data_documents_trl_701_trl_701 [INFERRED 0.85]
- **Acquired Resistance Finding to Monitoring Response Pipeline** — evidence_mcp_server_data_documents_lit_504_lit_504, evidence_mcp_server_data_documents_int_901_int_901, evidence_mcp_server_data_documents_lit_504_acquired_resistance_mechanism, evidence_mcp_server_data_documents_int_901_ctdna_monitoring_strategy [EXTRACTED 1.00]
- **OTel Collector to Tempo/Prometheus to Grafana Observability Pipeline** — docker_compose, otel_collector_config, tempo, prometheus, grafana_provisioning_datasources_datasources [EXTRACTED 1.00]

## Communities (13 total, 2 thin omitted)

### Community 0 - "Governed Pipeline Core"
Cohesion: 0.14
Nodes (35): 20-step AI-DLC checklist, citation-validator, confidence-scorer, evidence-synthesizer, literature-agent, p3-triage-agent, query-planner, trial-agent (+27 more)

### Community 1 - "UI Backend Instrumentation"
Cohesion: 0.10
Nodes (17): BaseHTTPRequestHandler, http_server, subprocess, time, get_tracer(), init_telemetry(), _NoopCounter, _NoopHistogram (+9 more)

### Community 2 - "Evidence MCP Server"
Cohesion: 0.10
Nodes (26): collections, check_staleness(), _cosine(), evidence_review(), evidence_standards(), get_document(), _idf(), _keyword_score() (+18 more)

### Community 3 - "GLX-9081 Evidence Corpus"
Cohesion: 0.16
Nodes (26): BLG-999 Unverified Patient Forum Post (Unapproved Source), Unapproved GLX-9081 Dosing Protocol (Anecdotal, Excluded from Evidence), ctDNA Monitoring Strategy for Early Resistance Detection, INT-901 ctDNA Monitoring Strategy Memo (BIO-2026-009), INT-902 KRAS G12C Competitive Landscape Memo (CI-2024-017), GLX-9081 (KRAS G12C Inhibitor Compound), KRAS G12C (Drug Target), LIT-501 GLX-9081 Pooled Phase 2 Analysis in NSCLC (+18 more)

### Community 4 - "Retrieval Allowlist Hook"
Cohesion: 0.15
Nodes (10): invokes_retrieval_tool(), True only if curl/wget is actually the program being run in some sub-command,…, datetime, json, os, pathlib, re, shlex (+2 more)

### Community 5 - "Observability & Load-Test Stack"
Cohesion: 0.29
Nodes (11): Docker Compose - OTel/Prometheus/Tempo/Grafana Stack, Docker Compose - k6 InfluxDB/Grafana Stack, k6-grafana Service (Grafana 11.4.0), k6-influxdb Service (InfluxDB 1.8), Grafana Datasources Provisioning (Prometheus + Tempo), Grafana k6 Dashboards Provider Config, Grafana InfluxDB Datasource Provisioning, OTel Collector Config (+3 more)

### Community 6 - "UI Rendering Logic"
Cohesion: 0.24
Nodes (8): escapeHtml(), findingTemplate, form, renderFinding(), renderResult(), results, statusLine, submitBtn

### Community 7 - "Graphify Skill Docs"
Cohesion: 0.25
Nodes (9): graphify add & watch reference, graphify exports & benchmark reference, graphify GitHub clone & cross-repo merge reference, graphify commit-hook & CLAUDE.md integration reference, graphify query/path/explain reference, graphify transcribe reference, graphify update & cluster-only reference, graphify skill (+1 more)

### Community 8 - "UI Presentation Layer"
Cohesion: 0.40
Nodes (6): frontend-agent, Fixed structured JSON response schema, ui/index.html, app.js, style.css (frontend), ui/server.py (headless pipeline backend), OpenTelemetry + Grafana Observability, OTel span/metrics instrumentation of ui/server.py

### Community 9 - "k6 Load Test Script"
Cohesion: 0.40
Nodes (4): ITERATIONS, options, VUS, ref_k6

### Community 10 - "Startup Script"
Cohesion: 0.50
Nodes (3): OTEL_EXPORTER_OTLP_ENDPOINT, OTEL_SERVICE_NAME, start.sh script

## Ambiguous Edges - Review These
- `Helios Evidence-Review Agent (CLAUDE.md governance spec)` → `Context-and-memory policy (key_points-only extraction discipline)`  [AMBIGUOUS]
  .claude/agents/literature-agent.md · relation: cites

## Knowledge Gaps
- **33 isolated node(s):** `/home/labuser/steve-proj/claude_training_pwc/ses4_4/evidence-mcp-server/.venv/bin/python`, `VUS`, `ITERATIONS`, `options`, `new-governed-agent-project.sh script` (+28 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 67 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `Helios Evidence-Review Agent (CLAUDE.md governance spec)` and `Context-and-memory policy (key_points-only extraction discipline)`?**
  _Edge tagged AMBIGUOUS (relation: cites) - confidence is low._
- **What connects `/home/labuser/steve-proj/claude_training_pwc/ses4_4/evidence-mcp-server/.venv/bin/python`, `VUS`, `ITERATIONS` to the rest of the system?**
  _33 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Governed Pipeline Core` be split into smaller, more focused modules?**
  _Cohesion score 0.13968253968253969 - nodes in this community are weakly interconnected._
- **Should `UI Backend Instrumentation` be split into smaller, more focused modules?**
  _Cohesion score 0.10344827586206896 - nodes in this community are weakly interconnected._
- **Should `Evidence MCP Server` be split into smaller, more focused modules?**
  _Cohesion score 0.09788359788359788 - nodes in this community are weakly interconnected._