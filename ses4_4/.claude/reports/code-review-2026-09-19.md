# Code review — 2026-09-19

Run via `/code-review` (effort: medium) against the Helios evidence-review
project while closing gaps against the 20-step AI-DLC checklist. All four
findings below were verified and fixed in this same pass — kept as a
record per this project's QA step (checklist step 12).

## Findings

1. **`scripts/new-governed-agent-project.sh`** — copied `.claude/settings.json`
   verbatim into scaffolded projects, but its PostToolUse audit-hook matcher
   hardcoded `mcp__evidence__<tool>` tool names. A scaffolded project's MCP
   server would never be named "evidence", so the audit hook would silently
   never fire — no audit trail at all in any project created from the
   scaffold.
   **Fix:** the script now retargets the matcher to `mcp__${DOMAIN_SLUG}__*`
   and tells the user (in its "Next steps" output) to register their MCP
   server under that exact key in `.mcp.json`.

2. **`.claude/hooks/enforce_source_allowlist.py`** — the Bash guard denied
   any command merely *containing the substring* `curl`, `wget`, `http://`,
   or `https://` anywhere in the command text, including inside an unrelated
   quoted argument (e.g. `grep -n "curl|wget|http" file.py`, or a `git
   commit -m` message mentioning a URL). Reproduced live during the review:
   a benign `grep` call was denied by this hook despite making no network
   request.
   **Fix:** rewritten to tokenize the full command with `shlex` first (so
   quoting is respected — a literal `|` inside a quoted string no longer
   gets mistaken for a shell pipe), split on real shell-operator tokens, and
   only treat a sub-command as a retrieval attempt when `curl`/`wget` is
   its actual first token (skipping common wrappers like `sudo`/`env`).
   Verified against 6 cases (3 benign, 3 real curl/wget/piped-fetch
   attempts) — all now classify correctly.

3. **`evidence-mcp-server/evidence_mcp_server.py`** — `list_sources()`
   returned every entry in `allowlist.json` unfiltered, including
   `unverified_forum_mirror` (`approved: false`), contradicting both its own
   docstring ("List every source on the **approved** allowlist") and the
   README's documented expectation that this call enumerates the 3
   approved sources.
   **Fix:** filters to `approved: true` entries, matching `search_corpus`
   and `get_document`'s existing filtering behavior.

4. **`CLAUDE.md`** — stated `BLG-999`'s source is "deliberately absent from
   `allowlist.json`," but `allowlist.json` actually lists it explicitly with
   `"approved": false`. The documented exclusion mechanism didn't match the
   real one, which would mislead anyone adding a similar exclusion for a new
   source.
   **Fix:** corrected the wording to describe the actual mechanism (an
   explicit `approved: false` flag, checked by `get_document`/
   `search_corpus`/`list_sources`).

## Outcome

All 4 findings fixed and spot-verified. No findings skipped.
