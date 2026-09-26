import datetime
import json
from pathlib import Path

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("corpus")

ALLOWLIST_PATH = Path(__file__).parent / "data" / "allowlist.json"
ALLOWLIST = json.loads(ALLOWLIST_PATH.read_text())
APPROVED_SOURCE_IDS = {s["source_id"] for s in ALLOWLIST["sources"] if s["approved"]}
STALENESS_THRESHOLD_DAYS = ALLOWLIST["staleness_threshold_days"]

# doc_id -> document. BLG-501's source_id is intentionally absent from allowlist.json,
# to prove the corpus itself enforces the allowlist, independent of any hook.
CORPUS = {
    "LIT-101": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "NX-14 receptor expression correlates with fibrotic tissue remodeling in murine models",
        "date": "2025-03-10",
        "body": (
            "Journal of Fibrotic Disease Research, Vol. 41. In bleomycin-induced lung "
            "fibrosis models, NX-14 receptor expression increased 3.2-fold in fibrotic "
            "tissue relative to healthy controls (p<0.01, n=24). Receptor density "
            "correlated with collagen deposition score (r=0.71). Authors conclude NX-14 "
            "is a plausible druggable target for anti-fibrotic therapy, pending "
            "confirmation of a causal (not merely correlative) role."
        ),
    },
    "LIT-102": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "Small-molecule NX-14 antagonism reduces collagen deposition in a rat fibrosis model",
        "date": "2025-08-22",
        "body": (
            "Journal of Fibrotic Disease Research, Vol. 46. Compound NCX-7401, a selective "
            "NX-14 receptor antagonist, reduced lung collagen content by 38% versus vehicle "
            "(n=18, p<0.05) in a 28-day rat bleomycin model. No significant change in "
            "hepatic or renal function panels was observed at the tested dose. Authors "
            "note the rodent dose was well below levels associated with off-target "
            "cardiac effects reported elsewhere in the NX-14 antagonist class."
        ),
    },
    "LIT-103": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "Off-target cardiac ion channel activity observed across the NX-14 antagonist chemical class",
        "date": "2026-01-14",
        "body": (
            "Journal of Cardiac Pharmacology, Vol. 12. Screening of six NX-14 receptor "
            "antagonists, including NCX-7401, against a hERG ion channel panel found "
            "measurable off-target inhibition (IC50 range 1.8-6.4 uM) across the class. "
            "Clinical relevance at therapeutic exposure is not yet established, but "
            "authors recommend cardiac safety monitoring in any human trial of this "
            "chemical class, including QT-interval assessment."
        ),
    },
    "LIT-104": {
        "source_id": "pubmed_central",
        "source_type": "literature",
        "title": "General review of receptor-family antagonists in fibrotic disease, 2023",
        "date": "2023-05-02",
        "body": (
            "Annual Review of Fibrosis Therapeutics. A broad survey of receptor-antagonist "
            "drug classes under investigation for pulmonary and hepatic fibrosis as of "
            "2023. NX-14 is mentioned once in a summary table as an 'emerging target' "
            "with no data cited. Included here as a low-relevance background reference, "
            "not primary evidence for any specific NX-14 claim."
        ),
    },
    "PAT-201": {
        "source_id": "uspto_patent_full_text",
        "source_type": "patent",
        "title": "US Patent 11,987,234 - Composition of matter: NX-14 receptor antagonist compounds",
        "date": "2024-02-20",
        "body": (
            "Assignee: NovaCure Therapeutics, Inc. Claims a genus of small-molecule "
            "compounds, including NCX-7401 (Example 14), that selectively antagonize the "
            "NX-14 receptor. Specification describes in vitro binding assays (Ki < 50 nM "
            "for NCX-7401) but does not disclose in vivo efficacy or safety data. Patent "
            "term extends to 2044."
        ),
    },
    "PAT-202": {
        "source_id": "uspto_patent_full_text",
        "source_type": "patent",
        "title": "US Patent 12,045,890 - Method of use: NX-14 antagonism for treatment of pulmonary fibrosis",
        "date": "2024-09-05",
        "body": (
            "Assignee: NovaCure Therapeutics, Inc. Claims methods of treating pulmonary "
            "fibrosis by administering an NX-14 receptor antagonist, citing the rat "
            "efficacy data later published as LIT-102 as supporting specification "
            "example data. Does not claim any specific dosing regimen for human "
            "administration."
        ),
    },
    "TRL-301": {
        "source_id": "clinicaltrials_gov",
        "source_type": "trial_registry",
        "title": "NCT-style registry entry: NCX-7401 Phase 1 single-ascending-dose safety study (completed)",
        "date": "2025-06-30",
        "body": (
            "Registry ID NCX7401-P1-001. Status: Completed. Randomized, placebo-controlled "
            "single-ascending-dose study of NCX-7401 in 36 healthy adult volunteers. "
            "Primary outcome: safety and tolerability. Results posted: no serious adverse "
            "events; two participants at the highest dose cohort showed transient, "
            "asymptomatic QT-interval prolongation that resolved without intervention. "
            "No efficacy endpoints were assessed in this study."
        ),
    },
    "TRL-302": {
        "source_id": "clinicaltrials_gov",
        "source_type": "trial_registry",
        "title": "NCT-style registry entry: NCX-7401 Phase 2 efficacy study in idiopathic pulmonary fibrosis (recruiting)",
        "date": "2026-04-01",
        "body": (
            "Registry ID NCX7401-P2-014. Status: Recruiting, not yet enrolling by invitation "
            "only. Randomized, double-blind, placebo-controlled study of NCX-7401 in "
            "patients with idiopathic pulmonary fibrosis. Primary outcome: change in "
            "forced vital capacity at 24 weeks. Estimated primary completion date: "
            "2027-09-30. No results are available yet; this entry describes trial design "
            "only, not outcomes."
        ),
    },
    "INT-401": {
        "source_id": "novacure_internal_docs",
        "source_type": "internal_report",
        "title": "NovaCure Internal Toxicology Memo TOX-2026-014: NCX-7401 90-day rat chronic toxicity update",
        "date": "2026-06-01",
        "body": (
            "Internal memo, NovaCure Preclinical Safety group. 90-day chronic dosing in "
            "rats at 3 dose levels found no dose-limiting toxicity at the intended "
            "clinical dose range. Mild, reversible elevation in liver enzymes observed "
            "at the highest dose only. Recommends continued monitoring of the hERG "
            "signal flagged in the published literature (see LIT-103) during any "
            "further clinical dosing."
        ),
    },
    "INT-402": {
        "source_id": "novacure_internal_docs",
        "source_type": "internal_report",
        "title": "NovaCure Internal Toxicology Memo TOX-2024-031: Early NCX-7401 in vitro cardiac safety screen",
        "date": "2024-11-01",
        "body": (
            "Internal memo, NovaCure Preclinical Safety group. Early in vitro cardiac "
            "safety screen of NCX-7401 found no significant hERG channel inhibition at "
            "the concentrations tested at the time. Note: this screen used a narrower "
            "concentration range than the later published class-wide screen (see "
            "LIT-103, 2026) and should not be treated as the current safety position on "
            "cardiac risk without cross-checking more recent data."
        ),
    },
    "BLG-501": {
        "source_id": "unverified_biorxiv_mirror",
        "source_type": "literature",
        "title": "[Unverified mirror] NCX-7401 shows dramatic efficacy in unpublished patient case series",
        "date": "2026-08-01",
        "body": (
            "Posted to a third-party preprint mirror site, not the original bioRxiv "
            "platform, and not peer-reviewed. Claims a small unpublished case series "
            "showing 'dramatic' improvement in three fibrosis patients given NCX-7401 "
            "off-label. No methodology, patient consent documentation, or data tables "
            "are provided. This source is not on the NovaCure approved-source allowlist."
        ),
    },
}


def _matches_query(doc: dict, query: str) -> bool:
    q = query.lower()
    return q in doc["title"].lower() or q in doc["body"].lower()


@mcp.tool()
def search_corpus(query: str, source_type: str | None = None) -> dict:
    """
    Search the approved evidence corpus by keyword. Read-only.
    source_type optionally filters to one of: literature, patent, trial_registry,
    internal_report. Only returns documents whose source_id is on the approved
    allowlist (see list_sources) - unapproved documents are silently excluded, even
    if they would otherwise match the query. Use this before citing any evidence.
    """
    results = []
    for doc_id, doc in CORPUS.items():
        if doc["source_id"] not in APPROVED_SOURCE_IDS:
            continue
        if source_type and doc["source_type"] != source_type:
            continue
        if not _matches_query(doc, query):
            continue
        results.append(
            {
                "doc_id": doc_id,
                "title": doc["title"],
                "source_type": doc["source_type"],
                "source_id": doc["source_id"],
                "date": doc["date"],
                "snippet": doc["body"][:200],
            }
        )
    return {"ok": True, "query": query, "count": len(results), "results": results}


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
    return {"ok": True, "policy_version": ALLOWLIST["policy_version"], "sources": ALLOWLIST["sources"]}


@mcp.tool()
def check_staleness(doc_id: str) -> dict:
    """
    Check whether a document exceeds the policy staleness threshold (see
    corpus://policy/evidence-standards). Read-only. Returns is_stale, age_days,
    and threshold_days. Call this on any internal_report document before relying
    on it to support a claim - a stale internal report must be disclosed as a gap.
    """
    doc = CORPUS.get(doc_id)
    if not doc:
        return {"ok": False, "error_type": "NOT_FOUND", "doc_id": doc_id}
    if doc["source_id"] not in APPROVED_SOURCE_IDS:
        return {"ok": False, "error_type": "SOURCE_NOT_APPROVED", "doc_id": doc_id}
    doc_date = datetime.date.fromisoformat(doc["date"])
    age_days = (datetime.date.today() - doc_date).days
    return {
        "ok": True,
        "doc_id": doc_id,
        "date": doc["date"],
        "age_days": age_days,
        "threshold_days": STALENESS_THRESHOLD_DAYS,
        "is_stale": age_days > STALENESS_THRESHOLD_DAYS,
    }


@mcp.resource("corpus://policy/evidence-standards")
def evidence_standards() -> str:
    """Return the current NovaCure evidence-review policy."""
    return f"""
NovaCure Evidence Review Policy v{ALLOWLIST['policy_version']}
- Retrieve only from approved sources: {", ".join(sorted(APPROVED_SOURCE_IDS))}.
- Ground every claim in a citation that resolves via get_document to an approved source.
- Return structured output: answer, confidence, citations, gaps.
- Fail gracefully: if approved evidence is insufficient or conflicting, say so - never
  fabricate a claim or fill a gap from general knowledge.
- Any internal_report older than {STALENESS_THRESHOLD_DAYS} days (see check_staleness)
  must be disclosed as a gap even when it is used to support an answer.
""".strip()


@mcp.prompt()
def evidence_review(research_question: str) -> str:
    """Reusable kickoff prompt for a governed NovaCure evidence review."""
    return f"""
You are the NovaCure evidence-review agent. Use only the connected corpus MCP tools
(search_corpus, get_document, list_sources, check_staleness) to answer the research
question below. Do not use general knowledge or the open web.

Return a structured result with: answer, confidence (high/medium/low) with rationale,
citations (each resolving to an approved doc_id), and gaps (missing, conflicting, or
stale evidence). If approved evidence is insufficient, set status to
insufficient_evidence rather than guessing.

Research question:
{research_question}
""".strip()


if __name__ == "__main__":
    mcp.run()
