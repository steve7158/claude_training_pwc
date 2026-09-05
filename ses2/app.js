(function () {
  "use strict";

  const API_BASE = "http://localhost:3001/api/audits";
  const SEARCH_API_BASE = "http://localhost:3001/api/search";

  const CRITERIA = [
    { key: "attributable", letter: "A", name: "Attributable", desc: "It is clear who performed the action or recorded the data, and when." },
    { key: "legible", letter: "L", name: "Legible", desc: "Data is readable, permanent, and free of unexplained alterations." },
    { key: "contemporaneous", letter: "C", name: "Contemporaneous", desc: "Data was recorded at the time the activity was performed." },
    { key: "original", letter: "O", name: "Original", desc: "Source data or a certified true copy is preserved; no unverified transcription." },
    { key: "accurate", letter: "A", name: "Accurate", desc: "Data is correct, truthful, and reflects the actual observation or event." },
    { key: "complete", letter: "+C", name: "Complete", desc: "All data is present, including repeat or reanalysis and any deleted/changed values." },
    { key: "consistent", letter: "+C", name: "Consistent", desc: "Data is internally consistent, chronologically sequenced, and time-stamped." },
    { key: "enduring", letter: "+E", name: "Enduring", desc: "Recorded on a durable medium and retained for the required record-retention period." },
    { key: "available", letter: "+A", name: "Available", desc: "Accessible for review, audit, or inspection throughout its retention period." },
  ];

  const RATINGS = [
    { key: "compliant", label: "Compliant", weight: 1 },
    { key: "minor", label: "Minor Gap", weight: 0.5 },
    { key: "major", label: "Major Gap", weight: 0 },
    { key: "na", label: "N/A", weight: null },
  ];

  const REFERENCE_COPY = {
    attributable: "Every entry must be traceable to the individual (or system) that made it, with a date/time stamp. Avoid shared logins and unsigned entries.",
    legible: "Records must remain readable for the full retention period. Original entries should never be obscured — corrections are struck through, not erased.",
    contemporaneous: "Record actions as they happen, not from memory afterward. Back-dating or batch-recording at the end of a shift is a common finding.",
    original: "Work from the first recording of data (raw data, primary record) or a verified true copy. Do not treat a transcription as the source.",
    accurate: "Data must be error-free and reflect what actually occurred, including correct calculations, units, and equipment calibration status.",
    complete: "Nothing may be omitted — including failed runs, out-of-specification results, or repeat testing. Audit trails must capture all changes.",
    consistent: "Timestamps and sequences of events must line up logically across related records (e.g., login, sample prep, and analysis times).",
    enduring: "Records must survive on durable media (validated systems, controlled paper) for the mandated retention period without degradation.",
    available: "Records must be retrievable for inspection or audit on request, in a readable format, without undue delay.",
  };

  let state = { audits: [], currentId: null, editingId: null, view: "dashboard" };

  async function refreshAudits() {
    try {
      const res = await fetch(API_BASE);
      if (!res.ok) throw new Error("Failed to load audits (" + res.status + ")");
      state.audits = await res.json();
    } catch (err) {
      alert("Could not reach the QA audit server at " + API_BASE + ".\n\n" + err.message);
      state.audits = [];
    }
  }

  function computeScore(criteriaResults) {
    let total = 0, count = 0;
    CRITERIA.forEach((c) => {
      const r = criteriaResults[c.key];
      const rating = RATINGS.find((x) => x.key === (r ? r.rating : null));
      if (rating && rating.weight !== null) {
        total += rating.weight;
        count += 1;
      }
    });
    if (count === 0) return null;
    return Math.round((total / count) * 100);
  }

  function statusFromScore(score) {
    if (score === null) return { key: "attention", label: "Incomplete" };
    if (score >= 90) return { key: "compliant", label: "Compliant" };
    if (score >= 70) return { key: "attention", label: "Needs Attention" };
    return { key: "noncompliant", label: "Non-Compliant" };
  }

  function fmtDate(d) {
    if (!d) return "";
    const dt = new Date(d + "T00:00:00");
    return dt.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  }

  // ---------- View switching ----------
  function showView(name) {
    document.querySelectorAll(".view").forEach((v) => v.classList.remove("active"));
    document.getElementById("view-" + name).classList.add("active");
    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.toggle("active", b.dataset.view === name);
    });
    state.view = name;
  }

  // ---------- Dashboard ----------
  function renderDashboard() {
    const audits = state.audits.slice().sort((a, b) => (b.updatedAt || "").localeCompare(a.updatedAt || ""));
    const scored = audits.map((a) => ({ audit: a, score: computeScore(a.criteria), }));

    const compliantCount = scored.filter((s) => statusFromScore(s.score).key === "compliant").length;
    const attentionCount = scored.filter((s) => statusFromScore(s.score).key === "attention").length;
    const noncompliantCount = scored.filter((s) => statusFromScore(s.score).key === "noncompliant").length;
    const withScore = scored.filter((s) => s.score !== null);
    const avgScore = withScore.length
      ? Math.round(withScore.reduce((sum, s) => sum + s.score, 0) / withScore.length)
      : 0;

    document.getElementById("stat-row").innerHTML = `
      <div class="stat-card accent">
        <div class="stat-value">${audits.length}</div>
        <div class="stat-label">Total Audits</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${avgScore}%</div>
        <div class="stat-label">Avg. Compliance Score</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${compliantCount}</div>
        <div class="stat-label">Compliant</div>
      </div>
      <div class="stat-card">
        <div class="stat-value">${attentionCount + noncompliantCount}</div>
        <div class="stat-label">Needs Attention / Non-Compliant</div>
      </div>
    `;

    const search = document.getElementById("search-input").value.trim().toLowerCase();
    const filter = document.getElementById("filter-status").value;

    let filtered = scored.filter(({ audit, score }) => {
      const status = statusFromScore(score).key;
      const matchesFilter = filter === "all" || status === filter;
      const haystack = `${audit.recordName} ${audit.recordType} ${audit.auditor}`.toLowerCase();
      const matchesSearch = !search || haystack.includes(search);
      return matchesFilter && matchesSearch;
    });

    const listEl = document.getElementById("audit-list");
    const emptyEl = document.getElementById("empty-state");

    if (audits.length === 0) {
      listEl.innerHTML = "";
      emptyEl.hidden = false;
      return;
    }
    emptyEl.hidden = true;

    if (filtered.length === 0) {
      listEl.innerHTML = `<div class="empty-state"><p>No audits match your search/filter.</p></div>`;
      return;
    }

    listEl.innerHTML = filtered.map(({ audit, score }) => {
      const status = statusFromScore(score);
      return `
        <div class="audit-row" data-id="${audit.id}">
          <div class="audit-row-main">
            <div class="audit-row-title">${escapeHtml(audit.recordName)}</div>
            <div class="audit-row-meta">${escapeHtml(audit.recordType)} • ${escapeHtml(audit.auditor)} • ${fmtDate(audit.date)}</div>
          </div>
          <div class="audit-row-right">
            <div class="score-mini">
              <div class="score-value">${score === null ? "—" : score + "%"}</div>
              <div class="score-label">Score</div>
            </div>
            <span class="badge badge-${status.key}">${status.label}</span>
          </div>
        </div>
      `;
    }).join("");

    listEl.querySelectorAll(".audit-row").forEach((row) => {
      row.addEventListener("click", () => openDetail(row.dataset.id));
    });
  }

  function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str || "";
    return div.innerHTML;
  }

  // ---------- New / Edit Audit Form ----------
  function renderCriteriaForm(existing) {
    const container = document.getElementById("criteria-container");
    container.innerHTML = CRITERIA.map((c) => {
      const current = existing && existing[c.key] ? existing[c.key] : { rating: null, note: "" };
      return `
        <div class="criterion" data-key="${c.key}">
          <div class="criterion-head">
            <div>
              <span class="criterion-name"><span class="criterion-letter">${c.letter}</span>${c.name}</span>
              <div class="criterion-desc">${c.desc}</div>
            </div>
            <div class="rating-group">
              ${RATINGS.map((r) => `<button type="button" class="rating-btn ${current.rating === r.key ? "active" : ""}" data-rating="${r.key}">${r.label}</button>`).join("")}
            </div>
          </div>
          <div class="criterion-notes">
            <textarea rows="2" placeholder="Evidence, observation, or gap description…">${escapeHtml(current.note)}</textarea>
          </div>
        </div>
      `;
    }).join("");

    container.querySelectorAll(".criterion").forEach((el) => {
      el.querySelectorAll(".rating-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
          el.querySelectorAll(".rating-btn").forEach((b) => b.classList.remove("active"));
          btn.classList.add("active");
        });
      });
    });
  }

  function collectCriteriaForm() {
    const result = {};
    document.querySelectorAll("#criteria-container .criterion").forEach((el) => {
      const key = el.dataset.key;
      const activeBtn = el.querySelector(".rating-btn.active");
      const note = el.querySelector("textarea").value.trim();
      result[key] = { rating: activeBtn ? activeBtn.dataset.rating : null, note };
    });
    return result;
  }

  function resetAuditForm() {
    document.getElementById("audit-form").reset();
    document.getElementById("f-date").value = new Date().toISOString().slice(0, 10);
    renderCriteriaForm(null);
    document.getElementById("audit-form-title").textContent = "New ALCOA+ Audit";
  }

  function openNewAuditForm() {
    state.editingId = null;
    resetAuditForm();
    showView("new-audit");
  }

  function openEditAuditForm(id) {
    const audit = state.audits.find((a) => a.id === id);
    if (!audit) return;
    state.editingId = id;
    document.getElementById("f-record-name").value = audit.recordName;
    document.getElementById("f-record-type").value = audit.recordType;
    document.getElementById("f-auditor").value = audit.auditor;
    document.getElementById("f-date").value = audit.date;
    document.getElementById("f-department").value = audit.department || "";
    document.getElementById("f-summary").value = audit.summary || "";
    renderCriteriaForm(audit.criteria);
    document.getElementById("audit-form-title").textContent = "Edit ALCOA+ Audit";
    showView("new-audit");
  }

  async function handleAuditFormSubmit(e) {
    e.preventDefault();
    const criteria = collectCriteriaForm();
    const record = {
      recordName: document.getElementById("f-record-name").value.trim(),
      recordType: document.getElementById("f-record-type").value,
      auditor: document.getElementById("f-auditor").value.trim(),
      date: document.getElementById("f-date").value,
      department: document.getElementById("f-department").value.trim(),
      summary: document.getElementById("f-summary").value.trim(),
      criteria,
    };

    if (!record.recordName || !record.recordType || !record.auditor || !record.date) {
      alert("Record Name, Record Type, Auditor Name, and Audit Date are required.");
      return;
    }

    const url = state.editingId ? `${API_BASE}/${state.editingId}` : API_BASE;
    const method = state.editingId ? "PUT" : "POST";

    try {
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(record),
      });
      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        throw new Error(body.error || `Save failed (${res.status})`);
      }
    } catch (err) {
      alert("Could not save audit: " + err.message);
      return;
    }

    state.editingId = null;
    await refreshAudits();
    renderDashboard();
    showView("dashboard");
  }

  // ---------- Detail View ----------
  function openDetail(id) {
    const audit = state.audits.find((a) => a.id === id);
    if (!audit) return;
    state.currentId = id;
    const score = computeScore(audit.criteria);
    const status = statusFromScore(score);

    document.getElementById("detail-title").textContent = audit.recordName;
    document.getElementById("detail-subtitle").textContent =
      `${audit.recordType} • ${audit.auditor} • ${fmtDate(audit.date)}${audit.department ? " • " + audit.department : ""}`;

    const rows = CRITERIA.map((c) => {
      const r = audit.criteria[c.key] || {};
      const ratingDef = RATINGS.find((x) => x.key === r.rating);
      const badgeClass = r.rating === "compliant" ? "badge-compliant"
        : r.rating === "minor" ? "badge-attention"
        : r.rating === "major" ? "badge-noncompliant"
        : "";
      return `
        <div class="detail-criterion">
          <div class="detail-criterion-left">
            <div class="detail-criterion-name"><span class="criterion-letter">${c.letter}</span>${c.name}</div>
            ${r.note ? `<div class="detail-criterion-note">${escapeHtml(r.note)}</div>` : ""}
          </div>
          ${ratingDef ? `<span class="badge ${badgeClass || "badge-na"}">${ratingDef.label}</span>` : `<span class="badge badge-unrated">Not Rated</span>`}
        </div>
      `;
    }).join("");

    document.getElementById("detail-content").innerHTML = `
      <div class="detail-summary-row">
        <div class="stat-card accent" style="flex:1;">
          <div class="stat-value">${score === null ? "—" : score + "%"}</div>
          <div class="stat-label">Compliance Score</div>
        </div>
        <div class="stat-card" style="flex:1;">
          <span class="badge badge-${status.key}" style="font-size:14px;padding:8px 16px;">${status.label}</span>
        </div>
      </div>
      ${audit.summary ? `<div class="card"><h2 class="card-title">Summary / Recommendations</h2><p style="margin:0;color:var(--ink-700);white-space:pre-wrap;">${escapeHtml(audit.summary)}</p></div>` : ""}
      <div class="card">
        <h2 class="card-title">ALCOA+ Assessment</h2>
        <div class="detail-criteria">${rows}</div>
      </div>
    `;

    showView("detail");
  }

  // ---------- Reference View ----------
  function renderReference() {
    document.getElementById("reference-container").innerHTML = CRITERIA.map((c) => `
      <div class="reference-card">
        <h3><span class="criterion-letter">${c.letter}</span>${c.name}</h3>
        <p>${REFERENCE_COPY[c.key]}</p>
      </div>
    `).join("");
  }

  // ---------- Wiring ----------
  function setSearchEmptyState(message) {
    const emptyEl = document.getElementById("search-empty-state");
    const resultsEl = document.getElementById("search-results");
    if (message) {
      document.getElementById("search-empty-message").textContent = message;
      emptyEl.hidden = false;
      resultsEl.innerHTML = "";
    } else {
      emptyEl.hidden = true;
    }
  }

  function renderSearchResults(results) {
    if (!results.length) {
      setSearchEmptyState("No results found.");
      return;
    }
    setSearchEmptyState(null);
    document.getElementById("search-results").innerHTML = results.map((r) => `
      <div class="search-result">
        ${r.url ? `<a class="search-result-title" href="${escapeHtml(r.url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(r.title)}</a>` : `<div class="search-result-title">${escapeHtml(r.title)}</div>`}
        ${r.url ? `<div class="search-result-url">${escapeHtml(r.url)}</div>` : ""}
        ${r.snippet ? `<p class="search-result-snippet">${escapeHtml(r.snippet)}</p>` : ""}
      </div>
    `).join("");
  }

  async function handleWebSearchSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("web-search-input");
    const query = input.value.trim();
    if (!query) return;

    const btn = document.getElementById("btn-web-search");
    btn.disabled = true;
    setSearchEmptyState("Searching…");

    try {
      const res = await fetch(SEARCH_API_BASE, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query }),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) throw new Error(body.error || `Search failed (${res.status})`);
      renderSearchResults(body.results || []);
    } catch (err) {
      setSearchEmptyState("Could not complete search: " + err.message);
    } finally {
      btn.disabled = false;
    }
  }

  async function init() {
    document.querySelectorAll(".tab-btn").forEach((btn) => {
      btn.addEventListener("click", () => showView(btn.dataset.view));
    });

    document.getElementById("btn-new-audit").addEventListener("click", openNewAuditForm);
    document.getElementById("btn-empty-new-audit").addEventListener("click", openNewAuditForm);
    document.getElementById("btn-cancel").addEventListener("click", () => {
      state.editingId = null;
      showView("dashboard");
    });
    document.getElementById("audit-form").addEventListener("submit", handleAuditFormSubmit);

    document.getElementById("btn-edit-audit").addEventListener("click", () => {
      if (state.currentId) openEditAuditForm(state.currentId);
    });
    document.getElementById("btn-delete-audit").addEventListener("click", async () => {
      if (!state.currentId) return;
      if (!confirm("Delete this audit? This cannot be undone.")) return;

      try {
        const res = await fetch(`${API_BASE}/${state.currentId}`, { method: "DELETE" });
        if (!res.ok && res.status !== 404) {
          const body = await res.json().catch(() => ({}));
          throw new Error(body.error || `Delete failed (${res.status})`);
        }
      } catch (err) {
        alert("Could not delete audit: " + err.message);
        return;
      }

      state.currentId = null;
      await refreshAudits();
      renderDashboard();
      showView("dashboard");
    });

    document.getElementById("search-input").addEventListener("input", renderDashboard);
    document.getElementById("filter-status").addEventListener("change", renderDashboard);

    document.getElementById("web-search-form").addEventListener("submit", handleWebSearchSubmit);

    renderReference();
    await refreshAudits();
    renderDashboard();
    showView("dashboard");
  }

  document.addEventListener("DOMContentLoaded", init);
})();
