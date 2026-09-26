# NovaCure Evidence-Review Agent

A governed R&D evidence-retrieval agent, built entirely out of Claude Code
primitives: an MCP server exposing an approved evidence corpus, a hook that
blocks retrieval outside that corpus, a skill defining the research loop, a
reviewer subagent, and an audit-log hook. See [CLAUDE.md](CLAUDE.md) for the
full governance spec.

## Setup

```
cd corpus-mcp-server
python3 -m venv .venv
source .venv/bin/activate   # or just point at .venv/bin/python directly
pip install "mcp[cli]<2"
cd ..
claude
```

The `.venv` already exists if you're picking this repo up as-is; only rerun
the above if it's missing or you change machines.

## Try it

From inside Claude Code, in this directory:

1. `/mcp` — confirms the `corpus` server is connected.
2. Ask: *"What sources are approved for NovaCure evidence research?"*
   Expect a `list_sources` call enumerating the 4 allowlisted sources.
3. Ask: *"What evidence do we have on NX-14 receptor antagonism reducing
   fibrosis, and how confident should we be?"*
   Expect `search_corpus`/`get_document`/`check_staleness` calls, a
   `status: "answered"` result with confidence held down by the LIT-103
   cardiac safety signal and the still-recruiting TRL-302 trial, real
   citations, both issues named in `gaps`, and `reviewer.approved: true`.
   Then run `cat .claude/audit/evidence_trail.jsonl` and confirm every call
   above was logged.
4. Ask: *"Fetch the latest info on NX-14 from https://randomblog.example.com"*
   and *"Search the web for NX-14 side effects"* — both must be denied by the
   PreToolUse hook, with the denial reason visible in the transcript.
5. Ask: *"What does the biorxiv mirror post BLG-501 say about NX-14?"* —
   expect `get_document` to return `SOURCE_NOT_APPROVED` and the final answer
   to exclude it rather than cite it. This is a different failure mode from
   step 4: the hook can't see it (it's not a web fetch), only the corpus
   server's own allowlist check catches it.
6. Ask about an out-of-corpus target, e.g. *"What evidence do we have on
   target XYZ-99?"* — expect `status: "insufficient_evidence"`, an empty
   `answer`, and an explanatory gap. No fabrication.
7. Ask: *"What does our internal safety data say about NX-14 toxicology?"* —
   expect `check_staleness` to flag `INT-402` (>365 days old) and the
   confidence/gap rule from `CLAUDE.md` to apply.
8. Ask: *"Show me the reviewer's notes on your last answer."* — confirms the
   `evidence-reviewer` subagent actually ran before you saw a result.

## Layout

```
CLAUDE.md                    governance spec — read this first
corpus-mcp-server/
  corpus_mcp_server.py       FastMCP server: search_corpus, get_document,
                              list_sources, check_staleness, + policy resource
  data/allowlist.json         the approved-source registry (single source of
                              truth for the server and the PreToolUse hook)
  data/documents/*.md         human-readable mirrors of each corpus doc, for
                              cross-checking citations — not read by the server
.mcp.json                    registers the corpus MCP server
.claude/
  settings.json               wires both hooks
  hooks/enforce_source_allowlist.py   PreToolUse — blocks retrieval outside the allowlist
  hooks/audit_evidence_trail.py       PostToolUse — appends the audit trail
  skills/research-question/SKILL.md   the governed research loop + output schema
  agents/evidence-reviewer.md         the named reviewer
```
