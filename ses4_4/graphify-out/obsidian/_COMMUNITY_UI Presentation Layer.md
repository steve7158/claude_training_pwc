---
type: community
cohesion: 0.40
members: 6
---

# UI Presentation Layer

**Cohesion:** 0.40 - moderately connected
**Members:** 6 nodes

## Members
- [[Fixed structured JSON response schema]] - concept - .claude/skills/evidence-review/SKILL.md
- [[OTel spanmetrics instrumentation of uiserver.py]] - rationale - OBSERVABILITY.md
- [[OpenTelemetry + Grafana Observability]] - document - OBSERVABILITY.md
- [[frontend-agent]] - concept - .claude/agents/frontend-agent.md
- [[uiindex.html, app.js, style.css (frontend)]] - concept - README.md
- [[uiserver.py (headless pipeline backend)]] - concept - README.md

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/UI_Presentation_Layer
SORT file.name ASC
```

## Connections to other communities
- 5 edges to [[_COMMUNITY_Governed Pipeline Core]]

## Top bridge nodes
- [[uiserver.py (headless pipeline backend)]] - degree 5, connects to 1 community
- [[frontend-agent]] - degree 4, connects to 1 community
- [[OpenTelemetry + Grafana Observability]] - degree 3, connects to 1 community
- [[Fixed structured JSON response schema]] - degree 2, connects to 1 community