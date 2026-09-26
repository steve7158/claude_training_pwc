import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

ALLOWLIST_PATH = Path(__file__).resolve().parents[2] / "corpus-mcp-server" / "data" / "allowlist.json"
ALLOWLIST = json.loads(ALLOWLIST_PATH.read_text())
APPROVED_DOMAINS = {s["domain"] for s in ALLOWLIST["sources"] if s["approved"] and s["domain"]}

DENY_REASON = (
    "Retrieval outside the approved NovaCure evidence corpus is blocked. "
    "Approved domains: " + ", ".join(sorted(APPROVED_DOMAINS)) + ". "
    "Use the corpus MCP tools (search_corpus, get_document, list_sources, "
    "check_staleness) instead."
)

URL_PATTERN = re.compile(r"https?://[^\s\"'<>]+")


def deny(reason: str) -> None:
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        }
    }))
    sys.exit(0)


def host_is_approved(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return any(host == d or host.endswith("." + d) for d in APPROVED_DOMAINS)


payload = json.load(sys.stdin)
tool_name = payload.get("tool_name", "")
tool_input = payload.get("tool_input", {}) or {}

if tool_name == "WebSearch":
    deny(DENY_REASON)

if tool_name == "WebFetch":
    url = tool_input.get("url", "")
    if not url or not host_is_approved(url):
        deny(DENY_REASON)

if tool_name == "Bash":
    command = tool_input.get("command", "")
    if re.search(r"\b(curl|wget)\b", command) or "http://" in command or "https://" in command:
        urls = URL_PATTERN.findall(command)
        if not urls or not all(host_is_approved(u) for u in urls):
            deny(DENY_REASON)

sys.exit(0)
