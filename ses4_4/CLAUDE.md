# Helios Evidence-Review Agent (Target/Disease Evidence POC)

A governed R&D evidence-retrieval agent for the business question: *"For
Target X / Disease Y, what evidence exists, how strong is it, and what are
the supporting sources?"* Given a target/disease pair, it answers only from
an approved corpus (PubMed-style literature, ClinicalTrials.gov-style trial
registry entries, internal research memos), grounds every claim in a
citation, scores confidence with a documented weighted formula, and fails
gracefully rather than fabricating. It supports a research decision; it does
not make one.

All corpus content is **synthetic demo data** for a fictional biotech
("Helios Oncology") and a fictional compound ("GLX-9081") targeting a real
drug-target class (KRAS G12C) in a real disease (NSCLC), so the demo reads
like a realistic evidence-review scenario. None of it is real published
literature, a real registered trial, or a real internal document — do not
treat any `doc_id` in this corpus as a real-world citation.

## Success criteria and where each one lives

| Success criterion | Implementation |
|---|---|
| Search only approved sources | `.claude/hooks/enforce_source_allowlist.py` (PreToolUse, blocks WebSearch/WebFetch/Bash-curl outside allowlisted domains) **and**, independently, `evidence-mcp-server/evidence_mcp_server.py`'s own allowlist check on every tool |
| Retrieve relevant literature across multiple repositories | `literature-agent` and `trial-agent` subagents, each scoped to one `source_type`, dispatched in parallel by the `evidence-review` skill (the supervisor) |
| Ground every answer with citations | `citation-validator` subagent — every `doc_id` must resolve via `get_document` before a claim survives |
| Provide confidence scoring | `confidence-scorer` subagent, fixed weighted formula (retrieval 30% / source quality 30% / cross-source agreement 20% / recency 20%), documented in full in `.claude/agents/confidence-scorer.md` |
| Return structured output (JSON/schema) | fixed schema in `.claude/skills/evidence-review/SKILL.md` — the supervisor never returns free text for this question type |
| Refuse unsupported claims | `evidence-synthesizer` drops any claim with zero resolving citations before it ever reaches the validator; `citation-validator` catches anything that slips through; the skill sets `status: "insufficient_evidence"` when the corpus has nothing relevant |

This is also the answer to "which rule belongs in CLAUDE.md, which in a
skill, which in a hook, which in a subagent": CLAUDE.md documents *why* and
*what's true*; the skill documents the *procedure* a pipeline run must
follow and the output contract; subagents each own one *pipeline stage* with
its own tool scope; hooks *enforce* deterministically what must never depend
on the model getting it right.

## Pipeline (mirrors the recommended architecture)

```
User question
    |
Supervisor Agent (.claude/skills/evidence-review/SKILL.md)
    |
    +-- query-planner            -> {target, disease, evidence_needed}
    |
    +-- literature-agent  --+
    +-- trial-agent        -+--> Hybrid search + re-ranking happens inside
    |                            search_corpus itself (keyword + TF-IDF
    |                            vector blend, then a recency boost)
    v
evidence-synthesizer  -> claims[] with consistency_score
    v
citation-validator    -> passed / rejected_doc_ids
    v
confidence-scorer     -> scored_claims[] (High/Medium/Low + numeric score)
    v
Supervisor assembles the fixed JSON response
```

Patents are deliberately out of scope for this POC (per the plan: "avoid
patents initially to reduce complexity") — there is no patent-agent and no
`patent` source_type in the corpus.

## The retrieval boundary vs. the corpus allowlist — two distinct layers

The hook governs **tool choice**: it stops any agent from reaching for the
open web (WebSearch, WebFetch, `curl`/`wget`) instead of the approved corpus.
The MCP server governs **its own data**: even inside the approved corpus,
one document (`BLG-999`, an unverified patient-forum mirror) has a
`source_id` listed in `allowlist.json` with `"approved": false`, so
`get_document`/`search_corpus`/`list_sources` all filter it out rather than
surface it. Both layers are
necessary — the hook can't see inside the corpus, and the corpus check can't
see a WebFetch attempt. Do not remove either on the assumption the other
covers it.

**`evidence-mcp-server/data/allowlist.json`, the server's allowlist checks,
and the hook's domain list all read the same file.** If you add or remove an
approved source, edit `allowlist.json` only — never hardcode a source name or
domain anywhere else in the server, the hooks, or a subagent prompt.

## Context & memory policy

Claude Code gives no API for a hard per-agent token budget, so this policy
is enforced through prompt contracts rather than a counter:

- **Per-subagent isolation is the memory allocation.** Each pipeline stage
  (`query-planner`, `literature-agent`, `trial-agent`,
  `evidence-synthesizer`, `citation-validator`, `confidence-scorer`) runs in
  its own fresh context with zero carryover from prior stages or prior
  pipeline runs — this is Claude Code subagent isolation, not something this
  project configures.
- **Cross-stage payloads are summaries, not raw documents.** `literature-agent`
  and `trial-agent` fetch full document bodies via `get_document` inside
  their own isolated context, but return only `key_points` (a handful of
  extractive bullets) to the caller — the full body never crosses into the
  supervisor's or `evidence-synthesizer`'s context. `evidence-synthesizer`
  re-fetches a document itself, on demand, only when a summary is
  insufficient — the same "expand on demand" pattern `citation-validator`
  already uses for its own verification pass. This is what keeps the
  historical/retrieved-document footprint a small fraction of any single
  stage's context window, rather than growing with corpus size.
- **The supervisor's own multi-turn window is where the 12-15%/last-8-10-turn
  guidance actually applies.** Each pipeline run's intermediate agent
  output (retrieval payloads, synthesis drafts, validator notes) is scratch
  work for that run only — once the final structured JSON is assembled, the
  supervisor should treat prior questions in the same session as "answered,"
  referencing only their final JSON output if the user follows up, not
  re-deriving from the intermediate stages of an earlier run.

## Tool integration

- **Internal/custom:** `evidence-mcp-server` (`evidence_mcp_server.py`) — the
  approved corpus, hybrid search, allowlist and staleness checks. Built for
  this project, not a third-party package.
- **Built-in/official Claude Code capabilities:** `/code-review`,
  `/security-review`, and this project's own `/triage` skill (dispatches
  `p3-triage-agent`) — reviewing and reporting, not part of the governed
  evidence-review pipeline itself.
- **External plugins:** none wired into this POC, deliberately. The
  3-source scope (literature, trial registry, internal reports) is fully
  served by the one internal MCP server; there's no external tool this
  pipeline needs that would justify the added surface area. (For an example
  of an external MCP plugin in this training repo, see the `fetch` MCP
  server wired into the sibling SIP Calculator project.)

## Metadata schema (Phase 1 ingestion contract)

Every corpus document is captured against the same metadata shape (also
exposed live via the `evidence://policy/metadata-schema` MCP resource):

```json
{
  "title": "",
  "authors": "",
  "publication_date": "",
  "source_type": "",
  "journal": "",
  "confidence_weight": ""
}
```

`confidence_weight` (0.0-1.0) is the per-document *source quality* input to
the confidence-scorer's formula — it is not a substitute for confidence
scoring, only one of its four weighted factors.

## Conventions

- Corpus documents live as an in-memory dict (`CORPUS`) in
  `evidence_mcp_server.py`, same pattern as
  `../ses3/rag-agent-specific/corpus-mcp-server/corpus_mcp_server.py` —
  the server owns the data. `evidence-mcp-server/data/documents/*.md` are
  human-readable mirrors only, generated for participants to cross-check
  citations against; the server never reads them, so keep them in sync by
  regenerating (see README) whenever you edit `CORPUS`.
- `check_staleness`'s threshold (`staleness_threshold_days` in
  `allowlist.json`) is the single source of truth for "how old is too old"
  for `internal_report` documents — don't duplicate the number elsewhere.
- Hybrid search (keyword overlap + TF-IDF cosine similarity, stdlib-only, no
  external embedding API) plus a small recency re-ranking boost both live
  inside `search_corpus` in the MCP server — there is deliberately no
  separate "re-ranking" MCP tool, to keep this POC's retrieval layer to one
  call site per the plan's reduced Phase 1-2 scope (Azure AI Search /
  `text-embedding-3-large` are the target production choice, not this POC).
- No automated test suite. Verify by running through the "Try it" section in
  `README.md` inside Claude Code.

## Stretch (not built, matches the plan's later phases)

- A dedicated `patent-agent` and `patent` source_type, once the POC expands
  past its initial 3-source scope.
- A real Azure AI Search / `text-embedding-3-large` backend behind
  `search_corpus`, replacing the stdlib TF-IDF approximation, without
  changing any agent's contract with the tool.
- Retrieval/precision evaluation harness against the metrics in the plan
  (Recall@10, Precision@10, Citation Coverage, Hallucination Rate) — not
  built here since it needs a labeled query set, which is beyond a 3-source,
  12-document demo corpus.
