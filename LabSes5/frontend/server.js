import path from "node:path";
import { fileURLToPath } from "node:url";

import express from "express";
import { createProxyMiddleware } from "http-proxy-middleware";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const BACKEND_URL = process.env.BACKEND_URL || "http://localhost:8000";
const PORT = process.env.PORT || 3000;

const app = express();

app.use(createProxyMiddleware({ pathFilter: "/api", target: BACKEND_URL, changeOrigin: true }));

app.use(express.static(path.join(__dirname, "dist")));

app.get("*", (req, res) => {
  res.sendFile(path.join(__dirname, "dist", "index.html"));
});

app.listen(PORT, () => {
  console.log(`UI server running at http://localhost:${PORT} (proxying /api -> ${BACKEND_URL})`);
});
