---
type: community
cohesion: 0.10
members: 28
---

# Evidence MCP Server

**Cohesion:** 0.10 - loosely connected
**Members:** 28 nodes

## Members
- [[Check whether a document exceeds the policy staleness threshold (see…]] - rationale - evidence-mcp-server/evidence_mcp_server.py
- [[Fetch the full content and metadata of one document by doc_id. Read-only.…]] - rationale - evidence-mcp-server/evidence_mcp_server.py
- [[Hybrid (keyword + TF-IDF vector) search over the approved evidence corpus, with…]] - rationale - evidence-mcp-server/evidence_mcp_server.py
- [[List every source on the approved allowlist (source_id, name, type, domain).…]] - rationale - evidence-mcp-server/evidence_mcp_server.py
- [[Return the Phase 1 ingestion metadata schema every document is captured against.]] - rationale - evidence-mcp-server/evidence_mcp_server.py
- [[Return the current Helios evidence-review policy.]] - rationale - evidence-mcp-server/evidence_mcp_server.py
- [[Reusable kickoff prompt for a governed targetdisease evidence review.]] - rationale - evidence-mcp-server/evidence_mcp_server.py
- [[_cosine()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[_doc_text()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[_idf()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[_keyword_score()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[_recency_boost()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[_tfidf_vector()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[_tokenize()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[check_staleness()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[collections]] - concept
- [[evidence_mcp_server.py]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[evidence_review()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[evidence_standards()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[get_document()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[list_sources()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[math]] - concept
- [[mcp_server_fastmcp]] - concept
- [[metadata_schema()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[prompt]] - code
- [[resource]] - code
- [[search_corpus()]] - code - evidence-mcp-server/evidence_mcp_server.py
- [[tool]] - code

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Evidence_MCP_Server
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Retrieval Allowlist Hook]]

## Top bridge nodes
- [[evidence_mcp_server.py]] - degree 21, connects to 1 community