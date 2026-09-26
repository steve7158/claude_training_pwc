---
type: community
cohesion: 0.15
members: 14
---

# Retrieval Allowlist Hook

**Cohesion:** 0.15 - loosely connected
**Members:** 14 nodes

## Members
- [[True only if curlwget is actually the program being run in some sub-command,…]] - rationale - .claude/hooks/enforce_source_allowlist.py
- [[audit_evidence_trail.py]] - code - .claude/hooks/audit_evidence_trail.py
- [[datetime]] - concept
- [[deny()]] - code - .claude/hooks/enforce_source_allowlist.py
- [[enforce_source_allowlist.py]] - code - .claude/hooks/enforce_source_allowlist.py
- [[host_is_approved()]] - code - .claude/hooks/enforce_source_allowlist.py
- [[invokes_retrieval_tool()]] - code - .claude/hooks/enforce_source_allowlist.py
- [[json]] - concept
- [[os]] - concept
- [[pathlib]] - concept
- [[re]] - concept
- [[shlex]] - concept
- [[sys]] - concept
- [[urllib_parse]] - concept

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Retrieval_Allowlist_Hook
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_UI Backend Instrumentation]]
- 4 edges to [[_COMMUNITY_Evidence MCP Server]]

## Top bridge nodes
- [[json]] - degree 4, connects to 2 communities
- [[pathlib]] - degree 3, connects to 2 communities
- [[sys]] - degree 3, connects to 1 community
- [[datetime]] - degree 2, connects to 1 community
- [[os]] - degree 2, connects to 1 community