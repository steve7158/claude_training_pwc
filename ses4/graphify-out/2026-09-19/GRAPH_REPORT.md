# Graph Report - ses4  (2026-09-19)

## Corpus Check
- Corpus is ~11,817 words - fits in a single context window. You may not need a graph.

## Summary
- 39 nodes · 45 edges · 6 communities (5 shown, 1 thin omitted)
- Extraction: 78% EXTRACTED · 20% INFERRED · 2% AMBIGUOUS · INFERRED: 9 edges (avg confidence: 0.84)
- Token cost: 117,932 input · 0 output

## Community Hubs (Navigation)
- SIP Backend & Dependencies
- SIP App Code Structure
- Graphify Skill Core & Flows
- Graphify Project Rules
- Extraction Spec & Honesty Rules
- MCP Server Configuration

## God Nodes (most connected - your core abstractions)
1. `Graphify Skill Definition` - 13 edges
2. `main()` - 4 edges
3. `app.py (Single-File Streamlit App)` - 4 edges
4. `Extraction Subagent Prompt Spec` - 4 edges
5. `Graphify Codebase-Question Rules` - 4 edges
6. `compute_sip_schedule()` - 3 edges
7. `render_growth_chart()` - 3 edges
8. `Backend Agent (SIP Calculator)` - 3 edges
9. `fetch MCP Tool` - 3 edges
10. `fetch` - 2 edges

## Surprising Connections (you probably didn't know these)
- `Graphify Skill Trigger Directive` --semantically_similar_to--> `Graphify Codebase-Question Rules`  [INFERRED] [semantically similar]
  .claude/CLAUDE.md → CLAUDE.md
- `matplotlib>=3.9` --conceptually_related_to--> `app.py (Single-File Streamlit App)`  [INFERRED]
  requirements.txt → .claude/agents/backend.md
- `pandas>=2.2` --conceptually_related_to--> `app.py (Single-File Streamlit App)`  [INFERRED]
  requirements.txt → .claude/agents/backend.md
- `streamlit>=1.38` --shares_data_with--> `app.py (Single-File Streamlit App)`  [INFERRED]
  requirements.txt → .claude/agents/backend.md
- `mcp-server-fetch>=2024.11` --shares_data_with--> `fetch MCP Tool`  [INFERRED]
  requirements.txt → .claude/agents/backend.md

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
Cohesion: 0.29
Nodes (9): compute_sip_schedule(), main(), SIP Calculator — Streamlit app. Computes the future value of a monthly…, render_breakdown_chart(), render_growth_chart(), DataFrame, matplotlib_pyplot, pandas (+1 more)

### Community 2 - "Graphify Skill Core & Flows"
Cohesion: 0.33
Nodes (6): Add URL & Watch Folder Flow, GitHub Clone & Cross-Repo Merge Flow, Video/Audio Transcription Flow, AST Structural Extraction (Part A), Graphify Skill Definition, God Nodes

### Community 3 - "Graphify Project Rules"
Cohesion: 0.40
Nodes (5): Graphify Skill Trigger Directive, Commit Hook & CLAUDE.md Integration, Query, Path & Explain Flow, Incremental Update & Cluster-Only Flow, Graphify Codebase-Question Rules

### Community 4 - "Extraction Spec & Honesty Rules"
Cohesion: 0.40
Nodes (5): Confidence Score Rubric, Node ID Format Rule, Extraction Subagent Prompt Spec, Honesty Rules, Semantic Extraction (Part B)

## Ambiguous Edges - Review These
- `fetch MCP Tool` → `Extra Exports and Benchmark`  [AMBIGUOUS]
  .claude/agents/backend.md · relation: conceptually_related_to

## Knowledge Gaps
- **10 isolated node(s):** `/home/labuser/steve-proj/claude_training_pwc/ses4/.venv/bin/python`, `AST Structural Extraction (Part A)`, `God Nodes`, `Add URL & Watch Folder Flow`, `GitHub Clone & Cross-Repo Merge Flow` (+5 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 17 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **1 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **What is the exact relationship between `fetch MCP Tool` and `Extra Exports and Benchmark`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **Why does `Graphify Skill Definition` connect `Community 2` to `Community 0`, `Community 3`, `Community 4`?**
  _High betweenness centrality (0.341) - this node is a cross-community bridge._
- **Why does `Extra Exports and Benchmark` connect `Community 0` to `Community 2`?**
  _High betweenness centrality (0.205) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `app.py (Single-File Streamlit App)` (e.g. with `matplotlib>=3.9` and `pandas>=2.2`) actually correct?**
  _`app.py (Single-File Streamlit App)` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 4 inferred relationships involving `Graphify Codebase-Question Rules` (e.g. with `Graphify Skill Trigger Directive` and `Commit Hook & CLAUDE.md Integration`) actually correct?**
  _`Graphify Codebase-Question Rules` has 4 INFERRED edges - model-reasoned connections that need verification._
- **What connects `/home/labuser/steve-proj/claude_training_pwc/ses4/.venv/bin/python`, `AST Structural Extraction (Part A)`, `God Nodes` to the rest of the system?**
  _10 weakly-connected nodes found - possible documentation gaps or missing edges._