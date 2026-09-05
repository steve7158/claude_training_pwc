const APIFY_MCP_URL = "https://mcp.apify.com/?tools=apify/rag-web-browser";
const TOOL_NAME = "apify--rag-web-browser";

let clientPromise = null;

class SearchNotConfiguredError extends Error {}

async function connect() {
  const token = process.env.APIFY_TOKEN;
  if (!token) throw new SearchNotConfiguredError("APIFY_TOKEN is not set");

  const { Client } = await import("@modelcontextprotocol/sdk/client/index.js");
  const { StreamableHTTPClientTransport } = await import("@modelcontextprotocol/sdk/client/streamableHttp.js");

  const transport = new StreamableHTTPClientTransport(new URL(APIFY_MCP_URL), {
    requestInit: { headers: { Authorization: `Bearer ${token}` } },
  });
  const client = new Client({ name: "alcoa-qa-audit-tool", version: "1.0.0" });
  await client.connect(transport);
  return client;
}

async function getClient() {
  if (!clientPromise) clientPromise = connect();
  try {
    return await clientPromise;
  } catch (err) {
    clientPromise = null;
    throw err;
  }
}

function extractJson(text) {
  try {
    return JSON.parse(text);
  } catch {
    return null;
  }
}

function normalizeResult(entry) {
  if (!entry || typeof entry !== "object") return null;
  const searchResult = entry.searchResult || entry;
  const title = searchResult.title || entry.title || entry.url || "Untitled";
  const url = searchResult.url || entry.url || "";
  const snippet = searchResult.description || entry.description || entry.snippet || (entry.markdown ? String(entry.markdown).slice(0, 300) : "");
  if (!url) return null;
  return { title: String(title), url: String(url), snippet: String(snippet) };
}

function normalizeToolResult(result) {
  const results = [];
  for (const block of result.content || []) {
    if (block.type !== "text") continue;
    const parsed = extractJson(block.text);
    if (Array.isArray(parsed)) {
      for (const entry of parsed) {
        const normalized = normalizeResult(entry);
        if (normalized) results.push(normalized);
      }
    } else if (parsed && typeof parsed === "object") {
      const normalized = normalizeResult(parsed);
      if (normalized) results.push(normalized);
    } else if (block.text && block.text.trim()) {
      results.push({ title: "Result", url: "", snippet: block.text.trim().slice(0, 500) });
    }
  }
  return results;
}

async function searchWeb(query, maxResults = 5) {
  let client;
  try {
    client = await getClient();
  } catch (err) {
    if (err instanceof SearchNotConfiguredError) throw err;
    clientPromise = null;
    client = await getClient();
  }

  let result;
  try {
    result = await client.callTool({ name: TOOL_NAME, arguments: { query, maxResults } });
  } catch (err) {
    clientPromise = null;
    throw err;
  }

  return normalizeToolResult(result);
}

module.exports = { searchWeb, SearchNotConfiguredError };
