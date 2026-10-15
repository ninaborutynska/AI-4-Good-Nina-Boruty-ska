"use client";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function Connection() {
  const [token, setToken] = useState("");
  const [message, setMessage] = useState("");
  const [saving, setSaving] = useState(false);
  const [status, setStatus] = useState<{ configured: boolean; connected: boolean; state: string } | null>(null);
  const [replacing, setReplacing] = useState(false);
  useEffect(() => {
    const check = async () => { try { const response = await fetch("/api/connection", { cache: "no-store" }); if (response.ok) setStatus(await response.json()); } catch { setMessage("Connection status is temporarily unavailable. Your saved key has not been removed."); } };
    void check(); const timer = setInterval(() => void check(), 15000); return () => clearInterval(timer);
  }, []);
  return <main><header><div><p className="eyebrow">LIVE DATA CONNECTION</p><h1>Connect GitHub</h1><p className="subtitle">Keep collected comments and completed sentiment results up to date.</p></div><Link className="button" href="/">← Dashboard</Link></header>
    <section className="panel"><h2>{!status ? "Checking saved connection…" : status.connected ? "Live synchronization is connected" : status.configured ? "Your GitHub key is saved" : "Configure private repository access"}</h2><p>The dashboard checks for new comments and completed analysis every 60 seconds. Collection continues independently. New comments can appear as awaiting analysis until the next GitHub analysis finishes.</p>
      {status?.configured && <p role="status">{status.state === "invalid_credentials" ? "GitHub rejected the saved key. It may have expired or been revoked. Replace it below." : status.state === "starting" ? "Synchronization is restarting automatically with your saved key. You do not need to enter it again." : status.state === "retrying" ? "Synchronization is temporarily unavailable and will retry automatically. You do not need to enter your key again." : "Your key is saved on this computer and reused automatically, including after restarting the app. The password field stays empty to keep the saved key private."}</p>}
      {status?.configured && <button type="button" onClick={() => setReplacing(value => !value)}>{replacing ? "Cancel replacement" : "Replace saved key"}</button>}
      {status && (!status.configured || replacing || status.state === "invalid_credentials") && <>
      <p>Create a <a href="https://github.com/settings/personal-access-tokens/new?name=Sentiment-dashboard&target_name=LuukAalders&expires_in=30&contents=read&actions=read" target="_blank" rel="noreferrer">fine-grained GitHub token</a> for <strong>LuukAalders/Hackathons</strong>, with <strong>Contents: Read-only</strong> and <strong>Actions: Read-only</strong>.</p>
      <form onSubmit={async event => { event.preventDefault(); setSaving(true); setMessage(""); try { const response = await fetch("/api/connection", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ token }) }); const result = await response.json(); if (response.ok) { setToken(""); setReplacing(false); setStatus({ configured: true, connected: false, state: "starting" }); setMessage("Key saved. You do not need to enter it again. Synchronization will check GitHub within 60 seconds."); } else setMessage(result.error); } catch { setMessage("Could not connect. Please try again."); } finally { setSaving(false); } }}>
        <label>GitHub access token<input type="password" value={token} onChange={event => setToken(event.target.value)} autoComplete="off" required style={{ display: "block", width: "100%", margin: "12px 0" }} /></label><button type="submit" disabled={saving}>{saving ? "Checking access…" : "Save local connection"}</button>
      </form></>}<p role="status">{message}</p><p className="muted">The token is stored only on this computer. It is never included in dashboard responses or uploaded to the repository.</p>
    </section></main>;
}
