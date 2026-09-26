import datetime
import math
from collections import Counter
from pathlib import Path
import json
import re

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("evidence")

ALLOWLIST_PATH = Path(__file__).parent / "data" / "allowlist.json"
ALLOWLIST = json.loads(ALLOWLIST_PATH.read_text())
APPROVED_SOURCE_IDS = {s["source_id"] for s in ALLOWLIST["sources"] if s["approved"]}
STALENESS_THRESHOLD_DAYS = ALLOWLIST["staleness_threshold_days"]

# doc_id -> document + metadata. All content below is a SYNTHETIC demo corpus for a
# fictional biotech ("Helios Oncology") and a fictional compound ("GLX-9081"); it is
# built for this POC only and must never be treated as real published literature.
#
# unverified_forum_mirror is intentionally absent from allowlist.json's approved set,
# to prove the corpus itself enforces the allowlist independent of any hook (BLG-999).
CORPUS = {
    "LIT-501": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "GLX-9081, a KRAS G12C inhibitor, demonstrates durable objective response in previously treated NSCLC: pooled phase 2 analysis",
        "authors": "Ramirez K, Okonkwo T, Fitzgerald S, et al.",
        "journal": "Journal of Thoracic Oncology (demo corpus)",
        "publication_date": "2025-11-02",
        "confidence_weight": 0.9,
        "body": (
            "Pooled analysis of two phase 2 cohorts (n=126) of GLX-9081 monotherapy in "
            "previously treated KRAS G12C-mutant NSCLC. Objective response rate 39% "
            "(95% CI 31-48%), median progression-free survival 6.9 months (95% CI "
            "5.8-8.1). Median overall survival not yet reached; follow-up remains "
            "immature. Adverse events were manageable, predominantly grade 1-2 GI "
            "toxicity. Authors conclude GLX-9081 monotherapy shows clinically "
            "meaningful, durable activity in this population."
        ),
    },
    "LIT-502": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "Intracranial activity of GLX-9081 in KRAS G12C-mutant NSCLC with brain metastases: a phase 2 subgroup analysis",
        "authors": "Fitzgerald S, Nasser R, Chu W, et al.",
        "journal": "Clinical Cancer Research (demo corpus)",
        "publication_date": "2026-02-14",
        "confidence_weight": 0.8,
        "body": (
            "Subgroup analysis (n=28) of patients with stable, previously treated "
            "brain metastases enrolled in the GLX-9081 phase 2 program. Intracranial "
            "objective response rate 32%, consistent with the systemic response rate "
            "reported in the main cohort (see LIT-501). No new CNS-specific safety "
            "signal was observed. Sample size is small; authors recommend confirmation "
            "in a dedicated CNS-metastasis cohort."
        ),
    },
    "LIT-503": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "Real-world effectiveness of the KRAS G12C inhibitor GLX-9081 in previously treated NSCLC: a multicenter retrospective cohort",
        "authors": "Okonkwo T, Bianchi L, Patel R, et al.",
        "journal": "Lung Cancer Research & Practice (demo corpus)",
        "publication_date": "2026-04-01",
        "confidence_weight": 0.7,
        "body": (
            "Retrospective multicenter cohort (n=214) of GLX-9081 use outside of "
            "clinical trials. Real-world objective response rate 31%, somewhat lower "
            "than the phase 2 trial population (see LIT-501), consistent with typical "
            "trial-to-real-world attenuation. Median follow-up was only 9 months at "
            "time of analysis, so median overall survival and long-term durability of "
            "response could not be estimated; the authors explicitly flag long-term "
            "survival data as immature and recommend longer follow-up before drawing "
            "durability conclusions."
        ),
    },
    "LIT-504": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "Acquired resistance mechanisms to GLX-9081 in KRAS G12C-mutant NSCLC: on-treatment biopsy analysis",
        "authors": "Chu W, Andersson M, Ramirez K, et al.",
        "journal": "Cancer Discovery (demo corpus)",
        "publication_date": "2026-01-20",
        "confidence_weight": 0.75,
        "body": (
            "Paired on-treatment biopsies (n=41) from patients progressing on "
            "GLX-9081 identified secondary RAS-pathway alterations in 55% of cases, "
            "emerging at a median of 10 months on therapy. Findings indicate that "
            "acquired resistance limits the durability of response over time and "
            "support prospective biomarker monitoring during treatment."
        ),
    },
    "LIT-505": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "Combination GLX-9081 plus anti-PD-1 checkpoint blockade in NSCLC: phase 1b safety signal of grade 3-4 hepatotoxicity",
        "authors": "Bianchi L, Nasser R, Okonkwo T, et al.",
        "journal": "Journal of Clinical Oncology (demo corpus)",
        "publication_date": "2026-05-10",
        "confidence_weight": 0.65,
        "body": (
            "Phase 1b dose-escalation of GLX-9081 combined with an anti-PD-1 "
            "checkpoint inhibitor in KRAS G12C-mutant NSCLC (n=32). Grade 3-4 "
            "hepatotoxicity occurred in 22% of patients on the combination, "
            "substantially higher than reported for GLX-9081 monotherapy (see "
            "LIT-501). The safety signal is specific to the combination arm; no "
            "increase in hepatotoxicity was observed for monotherapy dosing in this "
            "study. Authors recommend liver function monitoring for any combination "
            "regimen and caution against extrapolating combination safety from "
            "monotherapy data."
        ),
    },
    "LIT-506": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "Targeting RAS-pathway oncogenic drivers across solid tumors: a 2023 review",
        "authors": "Patel R, Andersson M.",
        "journal": "Annual Review of Oncogenic Signaling (demo corpus)",
        "publication_date": "2023-03-15",
        "confidence_weight": 0.5,
        "body": (
            "Broad survey of RAS-pathway-directed drug development as of 2023. "
            "KRAS G12C is mentioned once in a summary table as an 'emerging "
            "actionable target' with no data cited. Included here as low-relevance "
            "background, not primary evidence for any specific GLX-9081 or KRAS G12C "
            "efficacy or safety claim."
        ),
    },
    "TRL-701": {
        "source_id": "clinicaltrials_gov",
        "source_type": "trial_registry",
        "title": "Phase 2 registry entry: GLX-9081 monotherapy in previously treated KRAS G12C-mutant NSCLC (completed)",
        "authors": None,
        "journal": None,
        "publication_date": "2025-09-30",
        "confidence_weight": 0.9,
        "body": (
            "Registry ID HEL-9081-201. Status: Completed. Single-arm phase 2 study of "
            "GLX-9081 monotherapy in 126 patients with previously treated KRAS "
            "G12C-mutant NSCLC. Primary outcome (objective response rate): 39% "
            "(matches pooled analysis in LIT-501). Secondary outcome (median PFS): "
            "6.9 months. Overall survival follow-up is ongoing; OS data are not yet "
            "mature at the time of this registry update."
        ),
    },
    "TRL-702": {
        "source_id": "clinicaltrials_gov",
        "source_type": "trial_registry",
        "title": "Phase 3 registry entry: GLX-9081 versus docetaxel in second-line KRAS G12C-mutant NSCLC (completed)",
        "authors": None,
        "journal": None,
        "publication_date": "2026-03-18",
        "confidence_weight": 0.95,
        "body": (
            "Registry ID HEL-9081-301. Status: Completed. Randomized, open-label "
            "phase 3 study (n=345) comparing GLX-9081 to docetaxel in second-line "
            "KRAS G12C-mutant NSCLC. Primary outcome (PFS) met: hazard ratio 0.62 "
            "favoring GLX-9081 (95% CI 0.49-0.79). Overall survival is a key "
            "secondary endpoint; results are described as not yet mature, with "
            "follow-up ongoing at the time of this registry update."
        ),
    },
    "TRL-703": {
        "source_id": "clinicaltrials_gov",
        "source_type": "trial_registry",
        "title": "Phase 1/2 registry entry: GLX-9081 plus platinum-based chemotherapy in treatment-naive KRAS G12C-mutant NSCLC (recruiting)",
        "authors": None,
        "journal": None,
        "publication_date": "2026-07-01",
        "confidence_weight": 0.4,
        "body": (
            "Registry ID HEL-9081-104. Status: Recruiting, not yet enrolling by "
            "invitation only. Randomized study of GLX-9081 plus platinum-based "
            "chemotherapy versus chemotherapy alone in treatment-naive KRAS "
            "G12C-mutant NSCLC. Primary outcome: progression-free survival. No "
            "results are available; this entry describes trial design only."
        ),
    },
    "INT-901": {
        "source_id": "helios_internal_docs",
        "source_type": "internal_report",
        "title": "Helios Internal Biomarker Memo BIO-2026-009: circulating tumor DNA monitoring strategy for GLX-9081 resistance in KRAS G12C NSCLC",
        "authors": None,
        "journal": None,
        "publication_date": "2026-06-01",
        "confidence_weight": 0.6,
        "body": (
            "Internal memo, Helios Translational Biomarkers group. Proposes a "
            "ctDNA monitoring schedule for KRAS G12C-mutant NSCLC patients on "
            "GLX-9081, to detect the secondary RAS-pathway resistance alterations "
            "described in LIT-504 earlier in the treatment course, and support "
            "earlier clinical intervention on progression."
        ),
    },
    "INT-902": {
        "source_id": "helios_internal_docs",
        "source_type": "internal_report",
        "title": "Helios Internal Competitive Intelligence Memo CI-2024-017: early KRAS G12C inhibitor landscape assessment",
        "authors": None,
        "journal": None,
        "publication_date": "2024-08-01",
        "confidence_weight": 0.5,
        "body": (
            "Internal memo, Helios Competitive Intelligence group. Early-stage "
            "landscape assessment of KRAS G12C inhibitor competitors. Predates the "
            "phase 3 data in TRL-702 and the resistance findings in LIT-504; should "
            "not be treated as the current competitive or efficacy position without "
            "cross-checking more recent data."
        ),
    },
    "BLG-999": {
        "source_id": "unverified_forum_mirror",
        "source_type": "literature",
        "title": "[Unverified patient forum post] Anecdotal report of complete remission using an unapproved GLX-9081 dosing protocol",
        "authors": None,
        "journal": None,
        "publication_date": "2026-07-15",
        "confidence_weight": 0.0,
        "body": (
            "Posted to a third-party patient forum mirror, not a peer-reviewed or "
            "registry source. Describes a single unverified anecdote of 'complete "
            "remission' using an off-label GLX-9081 dosing protocol. No methodology, "
            "consent documentation, or data are provided. This source is not on the "
            "Helios approved-source allowlist and must never be cited as evidence."
        ),
    },
}

_WORD_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return _WORD_RE.findall(text.lower())


def _doc_text(doc: dict) -> str:
    return f"{doc['title']} {doc['body']}"


_DOC_TOKENS = {doc_id: _tokenize(_doc_text(doc)) for doc_id, doc in CORPUS.items()}
_DOC_COUNT = len(CORPUS)
_DF = Counter()
for _tokens in _DOC_TOKENS.values():
    for _term in set(_tokens):
        _DF[_term] += 1


def _idf(term: str) -> float:
    df = _DF.get(term, 0)
    return math.log((1 + _DOC_COUNT) / (1 + df)) + 1.0


def _tfidf_vector(tokens: list[str]) -> dict[str, float]:
    tf = Counter(tokens)
    return {term: count * _idf(term) for term, count in tf.items()}


def _cosine(a: dict[str, float], b: dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    common = set(a) & set(b)
    num = sum(a[t] * b[t] for t in common)
    denom_a = math.sqrt(sum(v * v for v in a.values()))
    denom_b = math.sqrt(sum(v * v for v in b.values()))
    if denom_a == 0 or denom_b == 0:
        return 0.0
    return num / (denom_a * denom_b)


_DOC_VECTORS = {doc_id: _tfidf_vector(tokens) for doc_id, tokens in _DOC_TOKENS.items()}


def _keyword_score(query_tokens: list[str], doc_tokens: list[str]) -> float:
    if not query_tokens:
        return 0.0
    doc_set = set(doc_tokens)
    hits = sum(1 for t in set(query_tokens) if t in doc_set)
    return hits / len(set(query_tokens))


def _recency_boost(publication_date: str | None) -> float:
    if not publication_date:
        return 0.0
    age_days = (datetime.date.today() - datetime.date.fromisoformat(publication_date)).days
    if age_days < 180:
        return 0.05
    if age_days < 365:
        return 0.02
    return 0.0


@mcp.tool()
def search_corpus(query: str, source_type: str | None = None, top_k: int = 10) -> dict:
    """
    Hybrid (keyword + TF-IDF vector) search over the approved evidence corpus, with a
    lightweight recency re-ranking pass applied on top. Read-only. source_type
    optionally filters to one of: literature, trial_registry, internal_report. Only
    returns documents whose source_id is on the approved allowlist (see list_sources)
    - unapproved documents are silently excluded even if they would otherwise match.
    Each result includes a hybrid_score (0-1-ish) plus its keyword_score and
    vector_score components. Use this before citing any evidence, and always fetch
    the full document with get_document before relying on its content.
    """
    query_tokens = _tokenize(query)
    query_vector = _tfidf_vector(query_tokens)

    results = []
    for doc_id, doc in CORPUS.items():
        if doc["source_id"] not in APPROVED_SOURCE_IDS:
            continue
        if source_type and doc["source_type"] != source_type:
            continue
        kw = _keyword_score(query_tokens, _DOC_TOKENS[doc_id])
        vec = _cosine(query_vector, _DOC_VECTORS[doc_id])
        if kw == 0 and vec == 0:
            continue
        hybrid = 0.5 * kw + 0.5 * vec
        hybrid = min(1.0, hybrid + _recency_boost(doc["publication_date"]))
        results.append(
            {
                "doc_id": doc_id,
                "title": doc["title"],
                "source_type": doc["source_type"],
                "source_id": doc["source_id"],
                "publication_date": doc["publication_date"],
                "confidence_weight": doc["confidence_weight"],
                "keyword_score": round(kw, 3),
                "vector_score": round(vec, 3),
                "hybrid_score": round(hybrid, 3),
                "snippet": doc["body"][:220],
            }
        )
    results.sort(key=lambda r: r["hybrid_score"], reverse=True)
    return {"ok": True, "query": query, "count": len(results), "results": results[:top_k]}


@mcp.tool()
def get_document(doc_id: str) -> dict:
    """
    Fetch the full content and metadata of one document by doc_id. Read-only.
    Returns {"ok": false, "error_type": "NOT_FOUND"} if doc_id does not exist.
    Returns {"ok": false, "error_type": "SOURCE_NOT_APPROVED"} if the document exists
    but its source_id is not on the approved allowlist - such a document must never
    be cited as evidence. Always call this (or search_corpus) before citing content;
    never rely on a doc_id from outside this corpus.
    """
    doc = CORPUS.get(doc_id)
    if not doc:
        return {"ok": False, "error_type": "NOT_FOUND", "doc_id": doc_id}
    if doc["source_id"] not in APPROVED_SOURCE_IDS:
        return {
            "ok": False,
            "error_type": "SOURCE_NOT_APPROVED",
            "doc_id": doc_id,
            "source_id": doc["source_id"],
        }
    return {"ok": True, "doc_id": doc_id, **doc}


@mcp.tool()
def list_sources() -> dict:
    """
    List every source on the approved allowlist (source_id, name, type, domain).
    Read-only. Use this to confirm the scope of the approved corpus before
    answering a research question, and to explain the source trail to a user.
    """
    approved_sources = [s for s in ALLOWLIST["sources"] if s.get("approved")]
    return {"ok": True, "policy_version": ALLOWLIST["policy_version"], "sources": approved_sources}


@mcp.tool()
def check_staleness(doc_id: str) -> dict:
    """
    Check whether a document exceeds the policy staleness threshold (see
    evidence://policy/evidence-standards). Read-only. Returns is_stale, age_days,
    and threshold_days. Call this on any internal_report document (and any trial
    that is not yet completed) before relying on it to support a claim - a stale
    internal report must be disclosed as a gap/limitation.
    """
    doc = CORPUS.get(doc_id)
    if not doc:
        return {"ok": False, "error_type": "NOT_FOUND", "doc_id": doc_id}
    if doc["source_id"] not in APPROVED_SOURCE_IDS:
        return {"ok": False, "error_type": "SOURCE_NOT_APPROVED", "doc_id": doc_id}
    doc_date = datetime.date.fromisoformat(doc["publication_date"])
    age_days = (datetime.date.today() - doc_date).days
    return {
        "ok": True,
        "doc_id": doc_id,
        "publication_date": doc["publication_date"],
        "age_days": age_days,
        "threshold_days": STALENESS_THRESHOLD_DAYS,
        "is_stale": age_days > STALENESS_THRESHOLD_DAYS,
    }


@mcp.resource("evidence://policy/evidence-standards")
def evidence_standards() -> str:
    """Return the current Helios evidence-review policy."""
    return f"""
Helios Evidence Review Policy v{ALLOWLIST['policy_version']}
- Retrieve only from approved sources: {", ".join(sorted(APPROVED_SOURCE_IDS))}.
- Ground every claim in a citation that resolves via get_document to an approved source.
- Return structured output: research_question, findings[] (claim, confidence,
  confidence_score, sources[]), limitations[].
- Fail gracefully: if approved evidence is insufficient or conflicting, say so - never
  fabricate a claim or fill a gap from general knowledge.
- Any internal_report older than {STALENESS_THRESHOLD_DAYS} days, or any trial_registry
  entry that is not yet completed (see check_staleness / get_document), must be
  disclosed as a limitation even when it is used to support an answer.
""".strip()


@mcp.resource("evidence://policy/metadata-schema")
def metadata_schema() -> str:
    """Return the Phase 1 ingestion metadata schema every document is captured against."""
    return json.dumps(
        {
            "title": "",
            "authors": "",
            "publication_date": "",
            "source_type": "",
            "journal": "",
            "confidence_weight": "",
        },
        indent=2,
    )


@mcp.prompt()
def evidence_review(target: str, disease: str) -> str:
    """Reusable kickoff prompt for a governed target/disease evidence review."""
    return f"""
You are the Helios evidence-review supervisor. Follow the evidence-review skill's
governed pipeline (query-planner -> literature-agent + trial-agent -> evidence-synthesizer
-> citation-validator -> confidence-scorer) to answer: what evidence exists for
{target} in {disease}, how strong is it, and what are the supporting sources?

Use only the connected evidence MCP tools. Do not use general knowledge or the open web.
Return the fixed structured schema defined in the skill.
""".strip()


if __name__ == "__main__":
    mcp.run()
