import datetime
import json
import os
import sys

payload = json.load(sys.stdin)
os.makedirs(".claude/audit", exist_ok=True)

tool_response = payload.get("tool_response")
if isinstance(tool_response, dict):
    summary = {k: tool_response.get(k) for k in ("ok", "error_type", "doc_id", "count", "is_stale") if k in tool_response}
else:
    summary = tool_response

entry = {
    "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "tool_name": payload.get("tool_name"),
    "tool_input": payload.get("tool_input"),
    "tool_response_summary": summary,
    "cwd": payload.get("cwd"),
}

with open(".claude/audit/evidence_trail.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(entry) + "\n")

print(json.dumps({
    "hookSpecificOutput": {
        "hookEventName": "PostToolUse",
        "additionalContext": "Logged to .claude/audit/evidence_trail.jsonl",
    }
}))
