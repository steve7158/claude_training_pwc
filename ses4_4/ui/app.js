const form = document.getElementById("ask-form");
const submitBtn = document.getElementById("submit-btn");
const statusLine = document.getElementById("status-line");
const results = document.getElementById("results");
const findingTemplate = document.getElementById("finding-template");

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = document.getElementById("question").value.trim();
  if (!question) return;

  submitBtn.disabled = true;
  submitBtn.textContent = "Running pipeline…";
  statusLine.hidden = false;
  statusLine.className = "status-line status-loading";
  statusLine.textContent =
    "Dispatching query-planner → literature-agent + trial-agent → " +
    "evidence-synthesizer → citation-validator → confidence-scorer… " +
    "this can take a minute or two.";
  results.hidden = true;
  results.innerHTML = "";

  try {
    const response = await fetch("/api/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question }),
    });
    const payload = await response.json();
    if (payload.error) {
      renderError(payload);
    } else {
      renderResult(payload);
    }
  } catch (err) {
    renderError({ error: "Request failed.", detail: String(err) });
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Ask";
  }
});

function renderError(payload) {
  statusLine.hidden = false;
  statusLine.className = "status-line status-error";
  statusLine.textContent = payload.error || "Something went wrong.";
  results.hidden = false;
  results.innerHTML = "";
  const detail = payload.detail || payload.raw;
  if (detail) {
    const pre = document.createElement("pre");
    pre.className = "raw-error";
    pre.textContent = detail;
    results.appendChild(pre);
  }
}

function renderResult(data) {
  statusLine.hidden = true;

  const wrapper = document.createElement("div");

  const head = document.createElement("div");
  head.className = "result-head";

  const statusBadge = document.createElement("span");
  statusBadge.className = `status-badge status-${data.status}`;
  statusBadge.textContent = data.status;
  head.appendChild(statusBadge);

  const meta = document.createElement("div");
  meta.className = "result-meta";
  const qLine = document.createElement("div");
  qLine.innerHTML = `<strong>Question:</strong> ${escapeHtml(data.research_question ?? "")}`;
  const tdLine = document.createElement("div");
  tdLine.innerHTML = `<strong>Target:</strong> ${escapeHtml(data.target ?? "—")} &nbsp; <strong>Disease:</strong> ${escapeHtml(data.disease ?? "—")}`;
  meta.appendChild(qLine);
  meta.appendChild(tdLine);
  head.appendChild(meta);

  wrapper.appendChild(head);

  const findingsSection = document.createElement("div");
  findingsSection.className = "findings";
  const findings = data.findings || [];
  if (findings.length === 0) {
    const empty = document.createElement("p");
    empty.className = "empty-findings";
    empty.textContent = "No findings — the approved corpus did not support this question.";
    findingsSection.appendChild(empty);
  } else {
    findings.forEach((finding) => findingsSection.appendChild(renderFinding(finding)));
  }
  wrapper.appendChild(findingsSection);

  if (data.limitations && data.limitations.length) {
    const limSection = document.createElement("div");
    limSection.className = "limitations";
    const h = document.createElement("h3");
    h.textContent = "Limitations";
    limSection.appendChild(h);
    const ul = document.createElement("ul");
    data.limitations.forEach((l) => {
      const li = document.createElement("li");
      li.textContent = l;
      ul.appendChild(li);
    });
    limSection.appendChild(ul);
    wrapper.appendChild(limSection);
  }

  if (data.citation_validation) {
    const cv = data.citation_validation;
    const strip = document.createElement("div");
    strip.className = `citation-strip ${cv.passed ? "passed" : "failed"}`;
    strip.textContent = `Citation validation (${cv.validated_by || "citation-validator"}): ${cv.passed ? "passed" : "failed"} — ${cv.notes || ""}`;
    wrapper.appendChild(strip);
  }

  const details = document.createElement("details");
  details.className = "raw-json";
  const summary = document.createElement("summary");
  summary.textContent = "Raw JSON";
  details.appendChild(summary);
  const pre = document.createElement("pre");
  pre.textContent = JSON.stringify(data, null, 2);
  details.appendChild(pre);
  wrapper.appendChild(details);

  results.innerHTML = "";
  results.appendChild(wrapper);
  results.hidden = false;
}

function renderFinding(finding) {
  const node = findingTemplate.content.cloneNode(true);
  const card = node.querySelector(".finding-card");
  const badge = node.querySelector(".confidence-badge");
  const score = node.querySelector(".confidence-score");
  const claim = node.querySelector(".finding-claim");
  const chips = node.querySelector(".source-chips");

  badge.className = `confidence-badge confidence-${finding.confidence}`;
  badge.textContent = finding.confidence;
  score.textContent =
    typeof finding.confidence_score === "number" ? finding.confidence_score.toFixed(2) : "";
  claim.textContent = finding.claim;

  (finding.sources || []).forEach((src) => {
    const chip = document.createElement("span");
    chip.className = `source-chip source-${src.source_type}`;
    chip.title = src.title || "";
    chip.textContent = `${src.doc_id} · ${src.source_type} · ${src.publication_date || ""}`;
    chips.appendChild(chip);
  });

  return card;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
