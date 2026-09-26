#!/usr/bin/env python3
"""Stdlib-only web UI backend for the Helios evidence-review pipeline.

Serves the static frontend and a single POST /api/ask endpoint that drives
the existing evidence-review skill headlessly via the `claude` CLI. No new
pip dependency (matches the project's stdlib-only convention), and no
permission bypass: tool access for the headless run is limited to an
explicit allowlist (mirroring each subagent's own `tools:` frontmatter
scope), with everything else auto-denied via --permission-prompts none
rather than hanging on a prompt no one is there to answer.
"""
import json
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import otel_setup

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 8787
PIPELINE_TIMEOUT_SECONDS = 240

# Only what the supervisor turn needs to dispatch the pipeline. Each
# subagent further narrows this via its own frontmatter `tools:` list -
# this is the outer bound, not a replacement for that scoping.
ALLOWED_TOOLS = ",".join([
    "Task",
    "Skill",
    "Read",
    "mcp__evidence__search_corpus",
    "mcp__evidence__get_document",
    "mcp__evidence__list_sources",
    "mcp__evidence__check_staleness",
])

# Mirrors the fixed schema documented in
# .claude/skills/evidence-review/SKILL.md - passed to --json-schema so the
# pipeline's final turn is validated against this shape instead of the
# backend having to guess whether it came back as prose or a code fence.
RESULT_SCHEMA = {
    "type": "object",
    "properties": {
        "research_question": {"type": "string"},
        "target": {"type": ["string", "null"]},
        "disease": {"type": ["string", "null"]},
        "status": {
            "type": "string",
            "enum": ["answered", "insufficient_evidence", "escalated"],
        },
        "findings": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "claim": {"type": "string"},
                    "confidence": {
                        "type": "string",
                        "enum": ["High", "Medium", "Low"],
                    },
                    "confidence_score": {"type": "number"},
                    "sources": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "doc_id": {"type": "string"},
                                "title": {"type": "string"},
                                "source_type": {
                                    "type": "string",
                                    "enum": [
                                        "literature",
                                        "trial_registry",
                                        "internal_report",
                                    ],
                                },
                                "source_id": {"type": "string"},
                                "publication_date": {"type": "string"},
                            },
                            "required": [
                                "doc_id",
                                "title",
                                "source_type",
                                "source_id",
                                "publication_date",
                            ],
                        },
                    },
                },
                "required": ["claim", "confidence", "confidence_score", "sources"],
            },
        },
        "limitations": {"type": "array", "items": {"type": "string"}},
        "citation_validation": {
            "type": "object",
            "properties": {
                "validated_by": {"type": "string"},
                "passed": {"type": "boolean"},
                "notes": {"type": "string"},
            },
            "required": ["validated_by", "passed", "notes"],
        },
    },
    "required": [
        "research_question",
        "target",
        "disease",
        "status",
        "findings",
        "limitations",
        "citation_validation",
    ],
}

STATIC_FILES = {
    "/": "index.html",
    "/index.html": "index.html",
    "/app.js": "app.js",
    "/style.css": "style.css",
}

CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".css": "text/css; charset=utf-8",
}


def run_pipeline(question: str) -> dict:
    start = time.monotonic()
    tracer = otel_setup.get_tracer()
    with tracer.start_as_current_span("helios.run_pipeline") as span:
        result = _invoke_pipeline(question)
        status = result.get("status", "error") if isinstance(result, dict) else "error"
        span.set_attribute("helios.pipeline.status", status)
        otel_setup.record_pipeline_result(status, (time.monotonic() - start) * 1000)
        return result


def _invoke_pipeline(question: str) -> dict:
    cmd = [
        "claude",
        "-p",
        "--output-format", "json",
        "--permission-prompts", "none",
        "--allowedTools", ALLOWED_TOOLS,
        "--json-schema", json.dumps(RESULT_SCHEMA),
        question,
    ]
    try:
        proc = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=PIPELINE_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired:
        return {"error": f"Pipeline timed out after {PIPELINE_TIMEOUT_SECONDS}s."}
    except FileNotFoundError:
        return {"error": "The 'claude' CLI was not found on PATH."}

    if proc.returncode != 0:
        return {
            "error": "claude CLI exited with an error.",
            "detail": proc.stderr.strip()[-2000:],
        }

    try:
        envelope = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {
            "error": "Could not parse CLI output as JSON.",
            "raw": proc.stdout[-2000:],
        }

    if envelope.get("is_error"):
        return {
            "error": "Claude reported an error.",
            "detail": str(envelope.get("result", ""))[-2000:],
        }

    result_text = envelope.get("result", "")
    try:
        return json.loads(result_text)
    except json.JSONDecodeError:
        return {
            "error": "Pipeline did not return the expected structured JSON.",
            "raw": str(result_text)[:2000],
        }


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send_json(self, status: int, payload: dict):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?", 1)[0]
        filename = STATIC_FILES.get(path)
        if filename is None:
            self._send_json(404, {"error": "Not found."})
            return
        file_path = STATIC_DIR / filename
        body = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", CONTENT_TYPES[file_path.suffix])
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path != "/api/ask":
            self._send_json(404, {"error": "Not found."})
            return
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"
        try:
            body = json.loads(raw)
        except json.JSONDecodeError:
            self._send_json(400, {"error": "Invalid JSON body."})
            return
        question = str(body.get("question") or "").strip()
        if not question:
            self._send_json(400, {"error": "Missing 'question'."})
            return
        self._send_json(200, run_pipeline(question))


def main():
    otel_setup.init_telemetry()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"Helios evidence-review UI running at http://{HOST}:{PORT}")
    print(f"Driving pipeline in project root: {PROJECT_ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
