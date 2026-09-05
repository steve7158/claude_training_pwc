# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

A single-page ALCOA+ data-integrity audit tool for the Eli Lilly QA department. The frontend (`index.html`/`styles.css`/`app.js`) is static HTML/CSS/JS with no build step; it talks to the Express + SQLite backend in `server/` over `fetch()` — **the backend must be running for the frontend to work at all**, there is no offline/localStorage fallback.

## Running

Both pieces must be running, on their respective ports, at the same time:

```bash
# Backend (from server/) — must be up first, or the frontend UI will alert() on load
cd server && npm install   # first time only
npm start                  # or: npm run dev (auto-restart on change)

# Frontend — serve the project root statically and open index.html
python3 -m http.server 8811
```

Backend reads `PORT` and `DB_PATH` from `../.env.production` (`DB_PATH` is resolved relative to the project root, not `server/`). `DB_HOST` in that file is a leftover from an earlier plan to use a networked database — SQLite is file-based and doesn't use it.

There is no build, lint, or automated test suite for either half — verify frontend changes by loading the page in a browser (or driving it headlessly with Playwright/`chromium-cli`) with the backend running, and checking the console for JS errors; verify backend changes with `curl` against the running server (see Backend section below for the exact calls).

## Architecture

Three files, loaded directly by `index.html` — no modules/bundler:

- `index.html` — markup for all views. Every view is a `<section class="view" id="view-*">` inside `<main>`; only one has `.active` at a time (dashboard, new-audit, detail, reference). All are present in the DOM simultaneously and shown/hidden via CSS, not created/destroyed.
- `styles.css` — all styling, including the `--lilly-*` CSS custom properties (brand color tokens) at the top of the file. Status colors (compliant/attention/non-compliant → green/amber/red) are defined once as `--green`/`--amber`/`--red-status` and reused via `.badge-*` and `.rating-btn[data-rating=*].active` classes — keep new status-like UI consistent with these three, don't invent new colors.
- `app.js` — a single IIFE, no imports/exports. Key pieces:
  - `CRITERIA` — the ordered list of the 9 ALCOA+ principles (key, letter, name, description shown in the audit form and reference view). This is the single source of truth for what a "criterion" is; both the audit form and the detail view iterate over it.
  - `RATINGS` — the 4 possible ratings per criterion (`compliant` / `minor` / `major` / `na`) with numeric `weight` (`na` has `weight: null` and is excluded from scoring).
  - `REFERENCE_COPY` — explanatory text per criterion key, shown only in the Reference view.
  - `state` — in-memory app state (`audits` array, `currentId`, `editingId`, `view`). `state.audits` is populated from the backend via `refreshAudits()` (a `GET ${API_BASE}` fetch) — it is a cache of the last successful fetch, not a source of truth; every create/update/delete round-trips to the API first and then calls `refreshAudits()` again before re-rendering, rather than mutating `state.audits` locally. `API_BASE` (top of the file) is hardcoded to `http://localhost:3001/api/audits` — there's no build step to inject this per-environment, so deploying the frontend anywhere other than alongside a backend on `localhost:3001` means editing that constant by hand.
  - `showView(name)` — the only view-switching mechanism; toggles `.active` on the matching `#view-*` section and the matching `.tab-btn[data-view=name]`. Call this rather than touching `classList` directly when adding new navigation.
  - `computeScore(criteriaResults)` → percentage across only the *applicable* (non-N/A) criteria; `statusFromScore(score)` buckets that into compliant (≥90%) / attention (70–89%) / non-compliant (<70%). Both are pure functions re-derived from an audit's `criteria` object on every render — audits do not store a cached score/status, so changing the scoring thresholds or weights only requires editing these two functions.
  - Rendering is done via template-literal `innerHTML` swaps per view (`renderDashboard`, `renderCriteriaForm`, `openDetail`, `renderReference`), followed by re-attaching event listeners on the newly inserted elements (e.g. `.rating-btn` click handlers in `renderCriteriaForm`). There is no virtual DOM — if you add elements inside one of these template strings, you must also (re)bind their listeners after the `innerHTML` assignment, in the same function.
  - User-supplied text is always passed through `escapeHtml()` before being interpolated into an `innerHTML` template — follow this pattern for any new field to avoid XSS via stored audit data.

## Data model

Each audit object as returned by the API and cached in `state.audits`:

```js
{
  id, recordName, recordType, auditor, date, department, summary,
  criteria: { [criterionKey]: { rating: 'compliant'|'minor'|'major'|'na'|null, note: string } },
  updatedAt, // ISO timestamp, used to sort the dashboard list
  score, status // computed server-side on every read (see Backend); app.js also recomputes both client-side from `criteria` via its own computeScore/statusFromScore rather than trusting these fields — see the scoring.js note below
}
```

`criteria` always has all 9 keys from `CRITERIA` once a form is saved (unrated ones have `rating: null`, excluded from scoring same as `na`). The frontend never sends `id`/`updatedAt` on create/update — the backend assigns both.

## Backend (`server/`)

Express + `better-sqlite3`, CommonJS, no framework beyond Express itself:

- `db.js` — opens the SQLite file at `DB_PATH` (WAL mode) and creates the `audits` table (snake_case columns; `criteria` stored as a JSON `TEXT` blob) if missing. No migration system — schema changes mean editing this `CREATE TABLE` and handling existing rows manually.
- `scoring.js` — a deliberate duplicate of `app.js`'s `CRITERIA`/`RATINGS`/`computeScore`/`statusFromScore` (same 9 keys, same weights, same 90/70 thresholds), kept as plain data/functions with no shared module between frontend and backend since the frontend runs from `file://`/static-server with no bundler. **If you change scoring in one, change it in the other** — nothing enforces they stay in sync.
- `routes/audits.js` — REST CRUD mounted at `/api/audits`: `GET /`, `GET /:id`, `POST /`, `PUT /:id`, `DELETE /:id`. Every read response is enriched with a computed `score`/`status` (see `scoring.js`) that is never stored — same "derive on read, don't cache" pattern as the frontend. `POST`/`PUT` require `recordName`/`recordType`/`auditor`/`date` (400 otherwise); `criteria` is normalized via `normalizeCriteria()` to always contain all 9 keys with `rating`/`note` defaults, mirroring how the frontend's saved-audit shape always has all 9 keys.
- `server.js` — loads env from `../.env.production`, applies `cors()` (wide open, all origins — the frontend is served from a different port so needs CORS; tighten this if the backend is ever exposed beyond local dev), mounts the router under `/api/audits`, plus `GET /health`.

The frontend calls this API directly via `fetch()` (see `API_BASE` in `app.js`) — `app.js` no longer touches `localStorage`. It still recomputes `score`/`status` from `criteria` client-side (its own `computeScore`/`statusFromScore`) rather than trusting the `score`/`status` fields the API response already includes — both are correct and kept in sync by construction, this is just duplicated work, not a bug.
