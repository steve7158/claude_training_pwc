import json
import re
import shlex
import sys
from pathlib import Path
from urllib.parse import urlparse

ALLOWLIST_PATH = Path(__file__).resolve().parents[2] / "evidence-mcp-server" / "data" / "allowlist.json"
ALLOWLIST = json.loads(ALLOWLIST_PATH.read_text())
APPROVED_DOMAINS = {s["domain"] for s in ALLOWLIST["sources"] if s["approved"] and s["domain"]}

DENY_REASON = (
    "Retrieval outside the approved Helios evidence corpus is blocked. "
    "Approved domains: " + ", ".join(sorted(APPROVED_DOMAINS)) + ". "
    "Use the evidence MCP tools (search_corpus, get_document, list_sources, "
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


WRAPPER_TOKENS = {"sudo", "env", "command", "nohup", "time", "exec"}


SHELL_OPERATORS = {";", "&&", "||", "|", "&"}


def invokes_retrieval_tool(command: str) -> bool:
    """True only if curl/wget is actually the program being run in some
    sub-command, not merely a substring that appears inside a quoted
    argument (e.g. a grep pattern or commit message mentioning "curl" or a
    URL). Tokenize the WHOLE command with shlex first (so quoting is
    respected and a literal "|" inside a quoted string like
    "curl|wget|http" stays part of one token instead of being treated as a
    pipe), then split the resulting token list on standalone shell-operator
    tokens and check each sub-command's first real token (skipping common
    wrappers)."""
    try:
        tokens = shlex.split(command)
    except ValueError:
        tokens = command.split()

    sub_commands: list[list[str]] = [[]]
    for token in tokens:
        if token in SHELL_OPERATORS:
            sub_commands.append([])
        else:
            sub_commands[-1].append(token)

    for sub_tokens in sub_commands:
        for token in sub_tokens:
            if token in WRAPPER_TOKENS or "=" in token:
                continue
            if token in ("curl", "wget"):
                return True
            break  # first real token wasn't curl/wget - check next sub-command
    return False


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
    if invokes_retrieval_tool(command):
        urls = URL_PATTERN.findall(command)
        if not urls or not all(host_is_approved(u) for u in urls):
            deny(DENY_REASON)

sys.exit(0)
