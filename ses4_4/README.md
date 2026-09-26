# Helios Evidence-Review Agent

A governed target/disease evidence-review agent, built entirely out of
Claude Code primitives: an MCP server exposing an approved 3-source evidence
corpus with hybrid (keyword + vector) search, a hook that blocks retrieval
outside that corpus, five pipeline subagents (planner, two retrieval agents,
synthesizer, citation validator, confidence scorer), a supervisor skill that
orchestrates them, and an audit-log hook. See [CLAUDE.md](CLAUDE.md) for the
full governance spec and the mapping from the original POC plan's success
criteria to what's implemented here.

## Setup

```
cd evidence-mcp-server
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

1. `/mcp` — confirms the `evidence` server is connected.
2. Ask: *"What sources are approved for Helios evidence research?"* Expect a
   `list_sources` call enumerating the 3 allowlisted sources (PubMed
   Central, ClinicalTrials.gov, Helios internal docs) — plus, if you inspect
   `evidence-mcp-server/data/allowlist.json`, the 4th, unapproved source
   (`unverified_forum_mirror`) that step 6 exercises.
3. Ask the demo scenario question: *"What evidence supports KRAS G12C
   inhibitors in lung cancer?"* This should trigger the `evidence-review`
   skill and run the full pipeline: `query-planner` ->
   `literature-agent` + `trial-agent` (in parallel) -> `evidence-synthesizer`
   -> `citation-validator` -> `confidence-scorer` -> assembled JSON. Expect:
   - `status: "answered"`.
   - A monotherapy efficacy/durability finding around `High`/`Medium`
     confidence, citing multiple corroborating literature (`LIT-501`,
     `LIT-502`, `LIT-503`) and trial (`TRL-701`, `TRL-702`) documents.
   - A separate combination-therapy hepatotoxicity finding (from `LIT-505`)
     — the pipeline must not merge this into the monotherapy claim.
   - A resistance/durability-limiting finding (from `LIT-504`).
   - `limitations` naming: immature long-term overall-survival data (per
     `LIT-501`/`LIT-503`/`TRL-701`/`TRL-702`), the still-recruiting
     combination trial `TRL-703`, and the stale internal competitive memo
     `INT-902` if it was cited anywhere in the run.
   - `citation_validation.passed: true`.
   Then run `cat .claude/audit/evidence_trail.jsonl` and confirm every
   corpus tool call above was logged.
4. Ask: *"Fetch the latest GLX-9081 data from https://randomblog.example.com"*
   and *"Search the web for GLX-9081 side effects"* — both must be denied by
   the PreToolUse hook, with the denial reason visible in the transcript.
5. Ask: *"What does the patient forum post BLG-999 say about GLX-9081?"* —
   expect `get_document` to return `SOURCE_NOT_APPROVED` and the final
   answer to exclude it rather than cite it. This is a different failure
   mode from step 4: the hook can't see it (it's not a web fetch), only the
   corpus server's own allowlist check catches it.
6. Ask about an out-of-corpus pair, e.g. *"What evidence supports EGFR
   exon 19 deletion inhibitors in pancreatic cancer?"* — expect
   `status: "insufficient_evidence"`, an empty `findings` array, and an
   explanatory `limitations` entry. No fabrication.
7. Ask: *"What does Helios's internal competitive intelligence say about the
   KRAS G12C inhibitor landscape?"* — expect `check_staleness` to flag
   `INT-902` (>365 days old) and the confidence/limitations rule from
   `CLAUDE.md` to apply (any finding resting on it capped at `Low`, and the
   staleness named explicitly in `limitations`).
8. Ask: *"Show me the citation validator's notes on your last answer."* —
   confirms `citation-validator` actually ran before you saw a result.

## Triage

`/triage` dispatches `p3-triage-agent` for a manual, on-demand review of the
project: correctness issues plus Helios-specific governance-compliance
drift (allowlist bypass risk, citation-validator being skippable, schema
drift between `SKILL.md` and `ui/server.py`'s `RESULT_SCHEMA`). It never
runs automatically as part of the evidence-review pipeline. Reports land in
`.claude/reports/triage-<date>.md`.

## Reusable scaffold

`scripts/new-governed-agent-project.sh <target-dir> <domain-name> ["<business
question>"]` scaffolds a new governed-agent POC from this project's reusable
skeleton (the PreToolUse allowlist hook, the allowlist.json single source of
truth, and the CLAUDE.md section skeleton) into a fresh directory — see the
script's own comments for what it does and doesn't parameterize.

## Web UI

A minimal browser UI drives the same pipeline non-interactively, for
demoing without a Claude Code terminal session:

```
python3 ui/server.py
```

Then open `http://127.0.0.1:8787`, type a target/disease question (e.g. the
demo scenario in step 3 above), and submit. The backend shells out to the
`claude` CLI in headless print mode (`-p --output-format json`), scoped to
the pipeline's own tools via `--allowedTools` with `--permission-prompts
none` (anything outside that list is auto-denied — no permission bypass),
and renders the fixed structured schema as status/confidence badges,
finding cards with source citations, limitations, and the citation
validator's verdict. Every existing enforcement layer (the PreToolUse
allowlist hook, the MCP server's own allowlist, per-agent tool scoping)
still applies exactly as it does in an interactive session — the UI is a
presentation layer, not a second governance path. `frontend-agent` owns
`ui/index.html`/`app.js`/`style.css`; `ui/server.py`'s pipeline invocation
is out of its scope.

## Observability and load testing

See `OBSERVABILITY.md` for the full OpenTelemetry + Grafana setup
(`ui/server.py` optionally emits a `helios.run_pipeline` span and
`helios.pipeline.requests_total`/`duration_ms` metrics per request — no-op
if `opentelemetry-*` isn't installed). `./start.sh` brings up the Docker
Compose stack and runs the UI with telemetry enabled.

For load testing, `k6/load-test.js` exercises the same `/api/ask` endpoint
— and therefore the real pipeline, not a mock — so its default profile is
deliberately light (2 VUs, ~4 iterations; see the script's own comment).
`docker-compose.k6.yaml` brings up a separate InfluxDB + Grafana
(`localhost:3001`) with a k6 dashboard, mirroring the pattern in the
sibling `ses4` project:

```
docker compose -f docker-compose.k6.yaml up -d
k6 run k6/load-test.js
```

## Knowledge vault (Graphify)

`.claude/skills/graphify` (copied from `ses4`) turns this project into a
navigable knowledge graph. `graphify-out/` already exists (182 nodes, 298
edges, 13 communities — real project structure, not a placeholder run):
`obsidian/` is a full Obsidian vault, `graph.html` is a standalone
interactive viz, `graph.json` is the GraphRAG-ready graph, and
`GRAPH_REPORT.md` is the plain-language audit report (God Nodes, Surprising
Connections, communities, an honest `AMBIGUOUS`/knowledge-gaps section).
Ask a codebase question and, once `/graphify` is registered (a fresh
session picks it up automatically — it was added mid-session here, so this
session ran its steps manually instead of via the slash command),
`graphify query "<question>"` answers from the existing graph rather than
rebuilding it. Its `hook-guard` entries in `.claude/settings.json` are
no-ops if the `graphify` CLI isn't installed.

## Layout

```
CLAUDE.md                        governance spec — read this first
evidence-mcp-server/
  evidence_mcp_server.py         FastMCP server: search_corpus (hybrid
                                   keyword+vector search with recency
                                   re-ranking), get_document, list_sources,
                                   check_staleness, + 2 policy resources
  data/allowlist.json             the approved-source registry (single
                                   source of truth for the server and the
                                   PreToolUse hook)
  data/documents/*.md             human-readable mirrors of each corpus doc,
                                   for cross-checking citations — not read by
                                   the server (regenerate with the snippet
                                   below if you edit CORPUS)
.mcp.json                        registers the evidence MCP server
ui/
  server.py                      stdlib-only HTTP backend, drives the
                                   pipeline headlessly via `claude -p`;
                                   optional OTel span/metrics per request
  otel_setup.py                   optional OpenTelemetry init (no-op stubs
                                   if opentelemetry-* isn't installed)
  index.html, app.js, style.css   browser frontend for the fixed schema
                                   (owned by frontend-agent)
.claude/
  settings.json                   wires the allowlist/audit hooks + graphify's
  hooks/enforce_source_allowlist.py   PreToolUse — blocks retrieval outside the allowlist
  hooks/audit_evidence_trail.py       PostToolUse — appends the audit trail
  agents/query-planner.md             Agent 1: target/disease/evidence_needed extraction
  agents/literature-agent.md          Agent 2a: literature-only retrieval
  agents/trial-agent.md               Agent 2b: trial-registry-only retrieval
  agents/evidence-synthesizer.md      Agent 3: claim formation + consistency_score
  agents/citation-validator.md        Agent 4: every claim's citations must resolve
  agents/confidence-scorer.md         Agent 5: weighted confidence formula
  agents/frontend-agent.md            owns ui/index.html, app.js, style.css
  agents/p3-triage-agent.md           manual correctness + governance-compliance review
  skills/evidence-review/SKILL.md     the supervisor loop + fixed output schema
  skills/triage/SKILL.md              dispatches p3-triage-agent on demand
  reports/                            /code-review and /triage output land here
scripts/new-governed-agent-project.sh  scaffold a new governed-agent POC from this one
OBSERVABILITY.md                 OpenTelemetry + Grafana setup for ui/server.py
docker-compose.yaml, otel-collector-config.yaml,
  prometheus.yml, tempo.yaml, grafana/   the OTel/Grafana stack
k6/load-test.js                  light-profile load test against /api/ask
docker-compose.k6.yaml, k6-observability/   k6's own InfluxDB + Grafana stack
start.sh                         brings up the Docker stack, runs the UI with OTel env vars
```

## Regenerating the document mirrors

`data/documents/*.md` are generated from `CORPUS` in
`evidence_mcp_server.py`. After editing `CORPUS`, regenerate them from
`evidence-mcp-server/`:

```
.venv/bin/python - <<'PYEOF'
import evidence_mcp_server as e
for doc_id, doc in e.CORPUS.items():
    lines = [f"# {doc_id}: {doc['title']}", ""]
    lines.append(f"- **Source type:** {doc['source_type']}")
    lines.append(f"- **Source ID:** {doc['source_id']}")
    if doc.get("authors"):
        lines.append(f"- **Authors:** {doc['authors']}")
    if doc.get("journal"):
        lines.append(f"- **Journal:** {doc['journal']}")
    lines.append(f"- **Publication date:** {doc['publication_date']}")
    lines.append(f"- **Confidence weight:** {doc['confidence_weight']}")
    lines.append("")
    lines.append(doc["body"])
    lines.append("")
    open(f"data/documents/{doc_id}.md", "w").write("\n".join(lines))
PYEOF
```
