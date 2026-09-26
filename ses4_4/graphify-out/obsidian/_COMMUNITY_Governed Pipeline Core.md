---
type: community
cohesion: 0.14
members: 36
---

# Governed Pipeline Core

**Cohesion:** 0.14 - loosely connected
**Members:** 36 nodes

## Members
- [[dot-claudehooksaudit_evidence_trail.py (PostToolUse audit hook)]] - concept - README.md
- [[dot-claudehooksenforce_source_allowlist.py (PreToolUse hook)]] - concept - CLAUDE.md
- [[20-step AI-DLC checklist]] - concept - .claude/reports/code-review-2026-09-19.md
- [[Azure AI Search  text-embedding-3-large backend (stretch)]] - concept - CLAUDE.md
- [[BLG-999 (unapproved patient-forum mirror doc)]] - concept - CLAUDE.md
- [[Code review 2026-09-19 report]] - document - .claude/reports/code-review-2026-09-19.md
- [[Context-and-memory policy (key_points-only extraction discipline)]] - rationale - .claude/agents/literature-agent.md
- [[Evidence Review skill (pipeline supervisor)]] - document - .claude/skills/evidence-review/SKILL.md
- [[GLX-9081 (fictional compound)]] - concept - CLAUDE.md
- [[Helios Evidence-Review Agent (CLAUDE.md governance spec)]] - document - CLAUDE.md
- [[Helios Evidence-Review Agent README]] - document - README.md
- [[Helios Oncology (fictional biotech)]] - concept - CLAUDE.md
- [[Hybrid keyword+vector search with recency re-ranking]] - rationale - CLAUDE.md
- [[KRAS G12C (drug target class)]] - concept - CLAUDE.md
- [[NSCLC (disease)]] - concept - CLAUDE.md
- [[Phase 1 ingestion metadata schema]] - concept - CLAUDE.md
- [[Retrieval boundary vs. corpus allowlist (two distinct layers)]] - rationale - CLAUDE.md
- [[Retrievalprecision evaluation harness (stretch, not built)]] - concept - CLAUDE.md
- [[Triage skill]] - document - .claude/skills/triage/SKILL.md
- [[Weighted confidence-scoring formula]] - rationale - .claude/agents/confidence-scorer.md
- [[check_staleness (MCP tool)]] - concept - CLAUDE.md
- [[citation-validator]] - concept - .claude/agents/citation-validator.md
- [[confidence-scorer]] - concept - .claude/agents/confidence-scorer.md
- [[evidence-mcp-server  evidence_mcp_server.py]] - concept - CLAUDE.md
- [[evidence-mcp-serverdataallowlist.json (approved-source registry)]] - concept - CLAUDE.md
- [[evidence-synthesizer]] - concept - .claude/agents/evidence-synthesizer.md
- [[get_document (MCP tool)]] - concept - CLAUDE.md
- [[list_sources (MCP tool)]] - concept - CLAUDE.md
- [[literature-agent]] - concept - .claude/agents/literature-agent.md
- [[new-governed-agent-project.sh]] - code - scripts/new-governed-agent-project.sh
- [[new-governed-agent-project.sh script]] - code - scripts/new-governed-agent-project.sh
- [[p3-triage-agent]] - concept - .claude/agents/p3-triage-agent.md
- [[patent-agent  patent source_type (stretch, not built)]] - concept - CLAUDE.md
- [[query-planner]] - concept - .claude/agents/query-planner.md
- [[search_corpus (MCP tool)]] - concept - CLAUDE.md
- [[trial-agent]] - concept - .claude/agents/trial-agent.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Governed_Pipeline_Core
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_UI Presentation Layer]]
- 2 edges to [[_COMMUNITY_Graphify Skill Docs]]

## Top bridge nodes
- [[Helios Evidence-Review Agent README]] - degree 15, connects to 1 community
- [[Evidence Review skill (pipeline supervisor)]] - degree 10, connects to 1 community
- [[citation-validator]] - degree 9, connects to 1 community
- [[p3-triage-agent]] - degree 7, connects to 1 community
- [[query-planner]] - degree 5, connects to 1 community