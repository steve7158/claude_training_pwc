require("dotenv").config({ path: require("path").join(__dirname, "..", ".env.production") });

const express = require("express");
const cors = require("cors");
const auditsRouter = require("./routes/audits");
const searchRouter = require("./routes/search");

const app = express();
const PORT = process.env.PORT || 3001;

app.use(cors());
app.use(express.json());

app.get("/health", (req, res) => res.json({ status: "ok" }));
app.use("/api/audits", auditsRouter);
app.use("/api/search", searchRouter);

app.use((err, req, res, next) => {
  if (err.type === "entity.parse.failed" || err instanceof SyntaxError) {
    return res.status(400).json({ error: "Malformed JSON body" });
  }
  if (err.type === "entity.too.large") {
    return res.status(413).json({ error: "Request body too large" });
  }
  console.error(err);
  res.status(500).json({ error: "Internal server error" });
});

app.listen(PORT, () => {
  console.log(`ALCOA+ QA API listening on port ${PORT}`);
});
