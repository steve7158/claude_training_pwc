const path = require("path");
const Database = require("better-sqlite3");

const DB_PATH = process.env.DB_PATH
  ? path.resolve(__dirname, "..", process.env.DB_PATH)
  : path.join(__dirname, "data", "audits.db");

const db = new Database(DB_PATH);
db.pragma("journal_mode = WAL");

db.exec(`
  CREATE TABLE IF NOT EXISTS audits (
    id TEXT PRIMARY KEY,
    record_name TEXT NOT NULL,
    record_type TEXT NOT NULL,
    auditor TEXT NOT NULL,
    date TEXT NOT NULL,
    department TEXT,
    summary TEXT,
    criteria TEXT NOT NULL,
    updated_at TEXT NOT NULL
  )
`);

module.exports = db;
