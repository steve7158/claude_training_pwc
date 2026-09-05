const express = require("express");
const crypto = require("crypto");
const db = require("../db");
const { CRITERIA_KEYS, computeScore, statusFromScore } = require("../scoring");

const router = express.Router();

function rowToAudit(row) {
  const criteria = JSON.parse(row.criteria);
  const score = computeScore(criteria);
  return {
    id: row.id,
    recordName: row.record_name,
    recordType: row.record_type,
    auditor: row.auditor,
    date: row.date,
    department: row.department || "",
    summary: row.summary || "",
    criteria,
    updatedAt: row.updated_at,
    score,
    status: statusFromScore(score),
  };
}

function isNonEmptyString(v) {
  return typeof v === "string" && v.trim().length > 0;
}

function asString(v) {
  return typeof v === "string" ? v : "";
}

function normalizeCriteria(input) {
  const criteria = {};
  for (const key of CRITERIA_KEYS) {
    const entry = (input && input[key]) || {};
    criteria[key] = { rating: entry.rating || null, note: entry.note || "" };
  }
  return criteria;
}

router.get("/", (req, res) => {
  const rows = db.prepare("SELECT * FROM audits ORDER BY updated_at DESC").all();
  res.json(rows.map(rowToAudit));
});

router.get("/:id", (req, res) => {
  const row = db.prepare("SELECT * FROM audits WHERE id = ?").get(req.params.id);
  if (!row) return res.status(404).json({ error: "Audit not found" });
  res.json(rowToAudit(row));
});

router.post("/", (req, res) => {
  const { recordName, recordType, auditor, date, department, summary, criteria } = req.body || {};
  if (!isNonEmptyString(recordName) || !isNonEmptyString(recordType) || !isNonEmptyString(auditor) || !isNonEmptyString(date)) {
    return res.status(400).json({ error: "recordName, recordType, auditor, and date are required" });
  }
  const id = crypto.randomUUID();
  const updatedAt = new Date().toISOString();
  db.prepare(`
    INSERT INTO audits (id, record_name, record_type, auditor, date, department, summary, criteria, updated_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
  `).run(id, recordName, recordType, auditor, date, asString(department), asString(summary), JSON.stringify(normalizeCriteria(criteria)), updatedAt);

  res.status(201).json(rowToAudit(db.prepare("SELECT * FROM audits WHERE id = ?").get(id)));
});

router.put("/:id", (req, res) => {
  const existing = db.prepare("SELECT * FROM audits WHERE id = ?").get(req.params.id);
  if (!existing) return res.status(404).json({ error: "Audit not found" });

  const { recordName, recordType, auditor, date, department, summary, criteria } = req.body || {};
  if (!isNonEmptyString(recordName) || !isNonEmptyString(recordType) || !isNonEmptyString(auditor) || !isNonEmptyString(date)) {
    return res.status(400).json({ error: "recordName, recordType, auditor, and date are required" });
  }
  const updatedAt = new Date().toISOString();
  db.prepare(`
    UPDATE audits
    SET record_name = ?, record_type = ?, auditor = ?, date = ?, department = ?, summary = ?, criteria = ?, updated_at = ?
    WHERE id = ?
  `).run(recordName, recordType, auditor, date, asString(department), asString(summary), JSON.stringify(normalizeCriteria(criteria)), updatedAt, req.params.id);

  res.json(rowToAudit(db.prepare("SELECT * FROM audits WHERE id = ?").get(req.params.id)));
});

router.delete("/:id", (req, res) => {
  const result = db.prepare("DELETE FROM audits WHERE id = ?").run(req.params.id);
  if (result.changes === 0) return res.status(404).json({ error: "Audit not found" });
  res.status(204).end();
});

module.exports = router;
