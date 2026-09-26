---
name: Triage
description: Manually trigger a P3 triage pass over the Helios evidence-review project — correctness review plus governance-compliance drift check (allowlist, citation-validator routing, schema lockstep) — and write a dated report. Use when the user asks to triage, review governance compliance, or "run P3" on this project.
---

# Triage

Dispatch the `p3-triage-agent` subagent with the raw user request (or, if
none was given beyond "run triage", with "review the current state of the
project"). Do not run this automatically as part of the `evidence-review`
pipeline — it is a manual, on-demand check invoked by a human, not a pipeline
stage.

After the agent finishes, tell the user where the report landed
(`.claude/reports/triage-<date>.md`) and summarize in 2-3 sentences whether
anything needs immediate attention — don't restate the full report inline.
