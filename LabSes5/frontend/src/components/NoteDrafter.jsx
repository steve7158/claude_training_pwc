import { useState } from "react";

import { draftNote } from "../api.js";

export default function NoteDrafter({ patientId }) {
  const [rawText, setRawText] = useState("");
  const [draft, setDraft] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);

  async function handleDraft() {
    if (!rawText.trim()) {
      setError("Enter some encounter notes first.");
      return;
    }
    setLoading(true);
    setError("");
    setCopied(false);
    try {
      const res = await draftNote(patientId, rawText);
      setDraft(res.draft_note);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCopy() {
    try {
      await navigator.clipboard.writeText(draft);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {
      setError("Could not copy to clipboard.");
    }
  }

  return (
    <div className="note-drafter">
      <h2>Draft encounter note</h2>
      <textarea
        rows={6}
        placeholder="Type or paste raw encounter notes (e.g. dictated bullet points)..."
        value={rawText}
        onChange={(e) => setRawText(e.target.value)}
      />
      <button onClick={handleDraft} disabled={loading}>
        {loading ? "Drafting..." : "Draft note"}
      </button>
      {error && <p className="error">{error}</p>}

      {draft && (
        <div className="draft-output">
          <div className="draft-header">
            <h3>Draft SOAP note</h3>
            <button onClick={handleCopy}>{copied ? "Copied!" : "Copy"}</button>
          </div>
          <textarea
            rows={14}
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
          />
        </div>
      )}
    </div>
  );
}
