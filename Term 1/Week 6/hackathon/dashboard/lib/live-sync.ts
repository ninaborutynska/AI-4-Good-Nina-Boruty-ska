import "server-only";
import { readFile, stat } from "node:fs/promises";
import path from "node:path";
import { spawn } from "node:child_process";

export const liveDirectory = () => path.resolve(process.cwd(), process.env.LIVE_SYNC_DIR || "../runtime/live");
let lastStart = 0;

export async function connectionStatus() {
  const directory = liveDirectory();
  let configured = !!process.env.GITHUB_TOKEN;
  let credentialFile = process.env.GITHUB_TOKEN_FILE || path.join(directory, "github-token");
  try {
    const config = JSON.parse(await readFile(path.join(directory, "credentials.json"), "utf8"));
    credentialFile = process.env.GITHUB_TOKEN_FILE || config.token_file || credentialFile;
  } catch { /* The default saved credential is used when no external file is configured. */ }
  try { configured ||= (await stat(credentialFile)).size > 0; } catch { /* No saved key. */ }
  let status: { ok?: boolean; checked_at?: string; error?: string } = {};
  try { status = JSON.parse(await readFile(path.join(directory, "status.json"), "utf8")); } catch { /* Starting. */ }
  const timestamp = Date.parse(status.checked_at || "");
  const fresh = Number.isFinite(timestamp) && Date.now() - timestamp < 180000;
  const invalid = fresh && status.error?.startsWith("GitHub authentication failed.");
  const state = !configured ? "not_configured" : invalid ? "invalid_credentials" : !fresh ? "starting" : status.ok ? "connected" : "retrying";
  return { configured, connected: state === "connected", state, checkedAt: status.checked_at || null };
}

export async function ensureLiveSync() {
  const status = await connectionStatus();
  if (status.configured && status.state === "starting" && Date.now() - lastStart > 30000) {
    lastStart = Date.now();
    const root = path.resolve(process.cwd(), "..");
    const executable = path.join(root, ".venv", process.platform === "win32" ? "Scripts/python.exe" : "bin/python");
    // Python holds a process-wide file lock: a resumed or concurrently started bridge wins safely.
    const child = spawn(executable, ["sync_github_live.py"], { cwd: root, detached: true, windowsHide: true, stdio: "ignore" });
    child.on("error", () => { /* Keep the saved dataset; the next request can retry. */ });
    child.unref();
  }
  return status;
}
