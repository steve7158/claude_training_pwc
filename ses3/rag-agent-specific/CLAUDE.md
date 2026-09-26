# NovaCure Evidence-Review Agent

A governed R&D evidence-retrieval agent. Given a research question about a
NovaCure drug target or compound, it answers only from an approved corpus
(primary literature, patents, trial registries, internal reports), grounds
every claim in a citation, and fails gracefully rather than fabricating. It
supports a research decision; it does not make one.

## The four commitments

1. **Retrieve only from approved sources** — allowlist enforced by a hook.
2. **Ground every claim** — each resolves to an allowlist citation.
3. **Return structured output** — answer, confidence, citations, gaps.
4. **Fail gracefully** — refuse or escalate rather than fabricate.

## Where each commitment lives

| Commitment / pillar | Implementation |
|---|---|
| Retrieval refused outside approved sources | `.claude/hooks/enforce_source_allowlist.py` (PreToolUse, denies WebSearch/WebFetch/Bash-curl outside allowlist domains) |
| MCP-governed connection to the approved corpus | `corpus-mcp-server/corpus_mcp_server.py` (every tool checks `data/allowlist.json` itself, independent of the hook) |
| Named reviewer checks output before it informs a decision | `.claude/agents/evidence-reviewer.md` subagent |
| Inputs, sources, prompts, and outputs are recorded | `.claude/hooks/audit_evidence_trail.py` (PostToolUse, appends to `.claude/audit/evidence_trail.jsonl`) |
| The loop itself (trigger/steps/stop conditions/handoff) and structured output schema | `.claude/skills/research-question/SKILL.md` |

This is also the answer to "which rule belongs in CLAUDE.md, which in a skill,
which in a hook": CLAUDE.md documents *why* and *what's true*; the skill
documents the *procedure* an agent run must follow; hooks *enforce*
deterministically what must never depend on the model getting it right.

## The retrieval boundary vs. the corpus allowlist — two distinct layers

The hook governs **tool choice**: it stops the agent from reaching for the open
web (WebSearch, WebFetch, `curl`/`wget`) instead of the approved corpus. The
MCP server governs **its own data**: even inside the approved corpus, one
document (`BLG-501`, an unverified preprint mirror) has a `source_id` that is
deliberately absent from `allowlist.json`, so `get_document`/`search_corpus`
refuse to surface it. Both layers are necessary — the hook can't see inside
the corpus, and the corpus check can't see a WebFetch attempt. Do not remove
either on the assumption the other covers it.

**`data/allowlist.json`, the server's allowlist checks, and the hook's domain
list all read the same file.** If you add or remove an approved source, edit
`allowlist.json` only — never hardcode a source name or domain anywhere else
in the server or the hooks.

## Structured output schema

See `.claude/skills/research-question/SKILL.md` for the full schema and the
confidence/staleness rules. Summary: `research_question`, `status`
(`answered | insufficient_evidence | escalated`), `answer`, `confidence`
(`high | medium | low`) with `confidence_rationale`, `citations[]`, `gaps[]`,
and `reviewer` (the evidence-reviewer subagent's verdict).

## Conventions

- Corpus documents live as an in-memory dict in `corpus_mcp_server.py` (same
  pattern as `helios-mcp-server/travelops_mcp_server.py`'s `BOOKINGS`), not on
  disk — the server owns the data. `corpus-mcp-server/data/documents/*.md` are
  human-readable mirrors only, generated for participants to cross-check
  citations against; the server never reads them, so they can drift stale
  without breaking anything, but keep them in sync when you edit `CORPUS`.
- `check_staleness`'s threshold (`staleness_threshold_days` in
  `allowlist.json`) is the single source of truth for "how old is too old" —
  don't duplicate the number elsewhere.
- No automated test suite. Verify by running through the "Try it" section in
  `README.md` inside Claude Code.

## Stretch challenge (not built)

A second PreToolUse hook could gate `mcp__corpus__get_document` calls directly
against the allowlist, as defense-in-depth on top of the server's own check.
Deliberately not built here: it would duplicate the same enforcement the
server already does in code, which muddies the point of this exercise (four
*distinct* pillars, not one pillar reinforced twice). Worth trying as an
extension exercise.
