import "server-only";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { createHash } from "node:crypto";
import { ensureLiveSync } from "./live-sync";
import { combine, csv, latest, stats, validDate } from "./data";

const TTL = 60_000;
type Snapshot = {
  comments: ReturnType<typeof combine>["comments"]; quality: ReturnType<typeof combine>["quality"];
  overview: ReturnType<typeof stats>; monitoringStarted: string | null; monitoringEnds: string | null;
  lastCollection: string | null; lastRefresh: string; source: string; commit: string | null;
  evaluation: Record<string, unknown>;
  lastSync?: string | null;
};
type State = { snapshot: Snapshot | null; error: string | null; checkedAt: string; stale: boolean };
let cached: State | null = null;
let checked = 0;
let inflight: Promise<State> | null = null;
let lastCommit = "";

class SourceError extends Error {}
async function github(url: string, optional = false): Promise<string | null> {
  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new SourceError("GitHub access is not configured. Set GITHUB_TOKEN in the dashboard’s server environment.");
  const response = await fetch(url, { headers: { Authorization: `Bearer ${token}`, Accept: "application/vnd.github.raw+json", "X-GitHub-Api-Version": "2022-11-28" }, cache: "no-store", signal: AbortSignal.timeout(20000) });
  if (optional && response.status === 404) return null;
  if (!response.ok) throw new SourceError(response.status === 401 ? "GitHub authentication failed. Check the server token." : response.status === 404 ? "Repository or dataset not found, or the server token lacks access." : response.status === 403 || response.status === 429 ? "GitHub request limit or permission error. Retrying after the refresh interval." : "GitHub data could not be loaded. Retrying after the refresh interval.");
  return response.text();
}
async function load(previous: Snapshot | null): Promise<Snapshot> {
  const local = process.env.DATA_SOURCE === "local";
  let sha: string | null = null;
  let read: (file: string, optional?: boolean) => Promise<string | null>;
  if (local) {
    const syncDirectory = process.env.LIVE_SYNC_DIR ? path.resolve(process.cwd(), process.env.LIVE_SYNC_DIR) : null;
    const manifest = syncDirectory ? JSON.parse(await readFile(path.join(syncDirectory, "current.json"), "utf8")) : null;
    const directory = manifest ? manifest.data_directory : path.resolve(process.cwd(), process.env.LOCAL_DATA_DIR || "../data");
    const resultsDirectory = manifest ? directory : process.env.LOCAL_RESULTS_DIR ? path.resolve(process.cwd(), process.env.LOCAL_RESULTS_DIR) : directory;
    sha = manifest?.commit || null;
    read = async (file, optional = false) => {
      const selected = ["sentiment_results.csv", "processing_status.csv", "manual_labels.csv", "evaluation.json"].includes(file) ? resultsDirectory : directory;
      try { return await readFile(path.join(selected, file), "utf8"); }
      catch (error) { if (optional && (error as NodeJS.ErrnoException).code === "ENOENT") return null; throw new SourceError("Local dataset could not be read. Configure LOCAL_DATA_DIR with real collected comments."); }
    };
  } else {
    const repository = process.env.GITHUB_REPOSITORY || "LuukAalders/Hackathons";
    if (!/^[\w.-]+\/[\w.-]+$/.test(repository)) throw new SourceError("Invalid server repository configuration.");
    const ref = process.env.GITHUB_REF || "main";
    const commit = JSON.parse((await github(`https://api.github.com/repos/${repository}/commits/${encodeURIComponent(ref)}`))!);
    sha = commit.sha;
    if (!sha || !/^[a-f0-9]{40}$/.test(sha)) throw new SourceError("Invalid repository response.");
    if (sha === lastCommit && previous) return { ...previous, lastRefresh: new Date().toISOString() };
    const folder = process.env.GITHUB_DATA_PATH || "Hackathon 6/data";
    read = (file, optional = false) => github(`https://api.github.com/repos/${repository}/contents/${[...folder.split("/"), file].map(encodeURIComponent).join("/")}?ref=${sha}`, optional);
  }
  const [comments, predictions, status, monitoring, log, manual, evaluation] = await Promise.all([
    read("youtube_comments.csv"), read("sentiment_results.csv", true), read("processing_status.csv", true),
    read("monitoring_started.txt", true), read("collection_log.csv", true), read("manual_labels.csv", true), read("evaluation.json", true)
  ]);
  const started = validDate(monitoring?.trim());
  const merged = combine(csv(comments!, ["comment_id", "video_id", "text", "published_at", "collected_at"]),
    predictions ? csv(predictions, ["comment_id", "sentiment", "confidence", "model_version", "analysed_at"]) : [],
    status ? csv(status, ["comment_id", "status"]) : [], started);
  const overview = stats(merged.comments);
  // Collector log schemas may differ; only timestamp columns explicitly named as collection activity are used.
  const logTimes = log ? csv(log).flatMap(row => ["collected_at", "timestamp", "run_at", "finished_at"].map(key => validDate(row[key]))) : [];
  const labels = manual ? csv(manual, ["comment_id", "text", "manual_sentiment"]).filter(row =>
    ["Positive", "Neutral", "Negative"].includes(row.manual_sentiment) && row.relevance?.trim().toLowerCase() !== "no" && merged.comments.some(comment => comment.comment_id === row.comment_id && comment.text === row.text)) : [];
  const report = evaluation && labels.length ? JSON.parse(evaluation) : null;
  const hash = (value: string) => createHash("sha256").update(value, "utf8").digest("hex");
  const evaluationData = report && report.manual_count === new Set(labels.map(row => row.comment_id)).size &&
    report.manual_labels_sha256 === hash(manual!) && report.predictions_sha256 === hash(predictions || "") ? report : {
    status: "awaiting_manual_labels", manual_count: labels.length,
    message: labels.length ? "Manual labels are available. Run evaluate_sentiment.py to generate a current comparison report." : "No manual labels are available. Label at least 50 real comments independently; evaluation results will appear after the comparison script runs."
  };
  lastCommit = sha || "";
  return { ...merged, overview, monitoringStarted: started, monitoringEnds: started ? new Date(Date.parse(started) + 48 * 3600000).toISOString() : null,
    lastCollection: latest([overview.lastCollection, ...logTimes]), lastRefresh: new Date().toISOString(),
    source: local ? process.env.LIVE_SYNC_DIR ? "Live GitHub synchronization" : "Local CSV files" : "Private GitHub repository", commit: sha, evaluation: evaluationData };
}
async function liveStatus(): Promise<{ error: string | null; checkedAt: string | null }> {
  if (!process.env.LIVE_SYNC_DIR) return { error: null, checkedAt: null };
  try {
    const status = JSON.parse(await readFile(path.resolve(process.cwd(), process.env.LIVE_SYNC_DIR, "status.json"), "utf8"));
    if (!status.ok) return { error: "Live GitHub synchronization needs attention. Open Connection to check access. Showing the last complete dataset.", checkedAt: status.checked_at || null };
    if (!validDate(status.checked_at) || Date.now() - Date.parse(status.checked_at) > 180_000)
      return { error: "Live synchronization has stopped checking GitHub. Showing the last complete dataset.", checkedAt: status.checked_at || null };
    return { error: null, checkedAt: status.checked_at };
  } catch { return { error: "Live synchronization is starting or needs configuration. Open Connection to check access.", checkedAt: null }; }
}
export async function getData(): Promise<State> {
  if (process.env.DATA_SOURCE === "local" && process.env.LIVE_SYNC_DIR) await ensureLiveSync();
  if (cached && Date.now() - checked < TTL) return cached;
  if (inflight) return inflight;
  inflight = (async () => {
    const checkedAt = new Date().toISOString();
    try {
      const snapshot = await load(cached?.snapshot || null);
      const sync = await liveStatus();
      cached = { snapshot: { ...snapshot, lastSync: sync.checkedAt }, error: sync.error, checkedAt, stale: !!sync.error };
    }
    catch (error) { cached = { snapshot: cached?.snapshot || null, error: error instanceof SourceError ? error.message : "Data could not be validated or loaded. Check the CSV files and server connection.", checkedAt, stale: !!cached?.snapshot }; }
    checked = Date.now(); return cached;
  })();
  try { return await inflight; } finally { inflight = null; }
}
