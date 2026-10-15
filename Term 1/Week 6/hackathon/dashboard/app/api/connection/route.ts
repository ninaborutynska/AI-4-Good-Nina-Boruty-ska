import { readFile, mkdir, writeFile, rename } from "node:fs/promises";
import path from "node:path";
import { ensureLiveSync, liveDirectory } from "@/lib/live-sync";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";
const directory = liveDirectory;

export async function GET() {
  const status = await ensureLiveSync();
  return Response.json({ ...status, ok: status.connected }, { headers: { "Cache-Control": "no-store" } });
}

export async function POST(request: Request) {
  // Only accept credential changes from this loopback app's same-origin page.
  const url = new URL(request.url);
  const origin = request.headers.get("origin");
  const host = request.headers.get("host");
  if (!origin || !host || !["localhost:3101", "127.0.0.1:3101", "[::1]:3101"].includes(host) || new URL(origin).host !== host || !["localhost", "127.0.0.1", "[::1]"].includes(url.hostname))
    return Response.json({ error: "Open this page from the local sentiment dashboard." }, { status: 403 });
  try {
    if (Number(request.headers.get("content-length") || 0) > 4096) throw new Error();
    const body = await request.json();
    const token = typeof body.token === "string" ? body.token.trim() : "";
    if (!/^[A-Za-z0-9_]{20,300}$/.test(token))
      return Response.json({ error: "Enter a valid GitHub token." }, { status: 400 });
    const headers = { Authorization: `Bearer ${token}`, Accept: "application/vnd.github+json" };
    const base = "https://api.github.com/repos/LuukAalders/Hackathons";
    const responses = await Promise.all(["/contents/Hackathon%206/data", "/actions/workflows/sentiment.yml/runs?per_page=1"].map(route => fetch(base + route, { headers, cache: "no-store", signal: AbortSignal.timeout(20000) })));
    if (responses.some(response => !response.ok))
      return Response.json({ error: "Access failed. Select Hackathons and grant Contents: Read and Actions: Read." }, { status: 400 });
    await mkdir(directory(), { recursive: true });
    const temporary = path.join(directory(), "github-token.new");
    await writeFile(temporary, token, { mode: 0o600 });
    await rename(temporary, path.join(directory(), "github-token"));
    await ensureLiveSync();
    return Response.json({ ok: true });
  } catch { return Response.json({ error: "The connection could not be saved. Check network access and try again." }, { status: 400 }); }
}
