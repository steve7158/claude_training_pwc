const express = require("express");
const { searchWeb, SearchNotConfiguredError } = require("../mcpApify");

const router = express.Router();

function isNonEmptyString(v) {
  return typeof v === "string" && v.trim().length > 0;
}

router.post("/", async (req, res) => {
  const { query } = req.body || {};
  if (!isNonEmptyString(query)) {
    return res.status(400).json({ error: "query is required" });
  }

  try {
    const results = await searchWeb(query.trim());
    res.json({ results });
  } catch (err) {
    if (err instanceof SearchNotConfiguredError) {
      return res.status(500).json({ error: "Search is not configured: set APIFY_TOKEN in .env.production" });
    }
    console.error(err);
    res.status(502).json({ error: "Web search is temporarily unavailable" });
  }
});

module.exports = router;
