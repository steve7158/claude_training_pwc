#!/usr/bin/env bash
# Scaffold a new governed-agent POC from the reusable skeleton this project
# (Helios evidence-review) established: a PreToolUse allowlist hook, an
# allowlist.json single source of truth shared between the hook and an MCP
# server, and the CLAUDE.md section skeleton documenting why/what for the
# pipeline.
#
# Usage: scripts/new-governed-agent-project.sh <target-dir> <domain-name> ["<one-line business question>"]
# Example: scripts/new-governed-agent-project.sh ../contracts-review-agent "Contract Review" \
#   "For Clause X in Contract Y, what precedent exists and how strong is it?"
set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <target-dir> <domain-name> [\"<one-line business question>\"]" >&2
  exit 1
fi

TARGET_DIR="$1"
DOMAIN_NAME="$2"
BUSINESS_QUESTION="${3:-For X, what evidence exists, how strong is it, and what are the supporting sources?}"
DOMAIN_SLUG=$(echo "$DOMAIN_NAME" | tr '[:upper:]' '[:lower:]' | tr -cs 'a-z0-9' '-' | sed 's/-$//')
MCP_SERVER_DIR="${DOMAIN_SLUG}-mcp-server"

SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [ -e "$TARGET_DIR" ]; then
  echo "Refusing to scaffold into an existing path: $TARGET_DIR" >&2
  exit 1
fi

SKILL_DIR="${DOMAIN_SLUG}"
case "$SKILL_DIR" in
  *-review) : ;;
  *) SKILL_DIR="${SKILL_DIR}-review" ;;
esac

mkdir -p "$TARGET_DIR/.claude/agents" \
         "$TARGET_DIR/.claude/hooks" \
         "$TARGET_DIR/.claude/skills/${SKILL_DIR}" \
         "$TARGET_DIR/.claude/audit" \
         "$TARGET_DIR/${MCP_SERVER_DIR}/data/documents"

# .claude/settings.json — same hook wiring pattern as this project's. The
# PostToolUse audit-hook matcher hardcodes tool names as
# "mcp__evidence__<tool>" (the "evidence" comes from this project's MCP
# server being registered under the key "evidence" in .mcp.json) - retarget
# that prefix to DOMAIN_SLUG so the matcher actually fires once you register
# your MCP server under that same key. If you register it under a different
# key, update this matcher to match.
sed "s/mcp__evidence__/mcp__${DOMAIN_SLUG}__/g" \
  "$SOURCE_DIR/.claude/settings.json" \
  > "$TARGET_DIR/.claude/settings.json"

# PreToolUse allowlist hook — copied verbatim; it already derives its
# approved-domain list from allowlist.json at runtime rather than hardcoding
# anything, so the only per-project edit needed is the deny-reason wording
# below (kept generic here on purpose — fill in your domain's tool names).
sed \
  -e "s/Helios evidence corpus/${DOMAIN_NAME} corpus/" \
  -e "s/evidence MCP tools (search_corpus, get_document, list_sources, /approved ${DOMAIN_NAME} MCP tools (search_corpus, get_document, list_sources, /" \
  -e "s#\"evidence-mcp-server\"#\"${MCP_SERVER_DIR}\"#" \
  "$SOURCE_DIR/.claude/hooks/enforce_source_allowlist.py" \
  > "$TARGET_DIR/.claude/hooks/enforce_source_allowlist.py"

cat > "$TARGET_DIR/${MCP_SERVER_DIR}/data/allowlist.json" <<EOF
{
  "sources": [
    {
      "source_id": "REPLACE_ME",
      "name": "REPLACE_ME approved source",
      "domain": "REPLACE_ME.example.com",
      "approved": true
    }
  ],
  "staleness_threshold_days": 365
}
EOF

cat > "$TARGET_DIR/CLAUDE.md" <<EOF
# ${DOMAIN_NAME} Agent (Governed Evidence-Review POC)

A governed agent for the business question: *"${BUSINESS_QUESTION}"*
Answers only from an approved corpus, grounds every claim in a citation,
scores confidence with a documented formula, and fails gracefully rather
than fabricating.

## Success criteria and where each one lives

| Success criterion | Implementation |
|---|---|
| Search only approved sources | \`.claude/hooks/enforce_source_allowlist.py\` (PreToolUse) **and** the MCP server's own allowlist check |
| Retrieve relevant evidence across repositories | scoped retrieval subagents, dispatched in parallel by the supervisor skill |
| Ground every answer with citations | a citation-validator subagent |
| Provide confidence scoring | a confidence-scorer subagent with a documented weighted formula |
| Return structured output | a fixed schema in the supervisor skill |
| Refuse unsupported claims | claims with zero resolving citations are dropped before reaching the validator |

## Context & memory policy

Each pipeline stage runs as an isolated subagent (no carryover). Retrieval
agents fetch full documents inside their own context but return only
extractive \`key_points\` summaries to the caller — never raw document
bodies — so cross-stage payloads stay small regardless of corpus size.

## Conventions

- \`${MCP_SERVER_DIR}/data/allowlist.json\` is the single source of truth for
  approved sources — never hardcode a source name/domain anywhere else.
- Fill in the pipeline diagram, metadata schema, and stretch-goals sections
  following the pattern in the Helios evidence-review project this was
  scaffolded from.
EOF

cat > "$TARGET_DIR/.claude/skills/${SKILL_DIR}/SKILL.md" <<EOF
---
name: ${DOMAIN_NAME} Review
description: TODO — describe the trigger question this skill answers and when to use it instead of general knowledge.
---

# ${DOMAIN_NAME} Review

TODO: define the supervisor loop (plan -> retrieve in parallel -> synthesize
-> validate citations -> score confidence -> assemble) and the fixed output
schema, following the pattern in \`.claude/skills/evidence-review/SKILL.md\`
in the Helios project this was scaffolded from.
EOF

cat > "$TARGET_DIR/.gitignore" <<'EOF'
**/.venv/
**/__pycache__/
.claude/audit/
EOF

echo "Scaffolded governed-agent project at: $TARGET_DIR"
echo "Next steps:"
echo "  1. Fill in ${MCP_SERVER_DIR}/data/allowlist.json with real approved sources."
echo "  2. Write the MCP server exposing search_corpus/get_document/list_sources/check_staleness,"
echo "     and register it in .mcp.json under the exact key \"${DOMAIN_SLUG}\" - the copied"
echo "     .claude/settings.json PostToolUse audit hook only matches mcp__${DOMAIN_SLUG}__* tool names."
echo "  3. Fill in .claude/skills/${SKILL_DIR}/SKILL.md and add retrieval/synthesis/validator/scorer agents."
echo "  4. .claude/settings.json also carries this project's graphify hook-guard entries (no-ops unless"
echo "     the graphify CLI is installed) - remove them if the new project won't use graphify."
