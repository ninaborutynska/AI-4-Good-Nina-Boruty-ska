import { parse } from "csv-parse/sync";

export const sentiments = ["Positive", "Neutral", "Negative"] as const;
export type Sentiment = typeof sentiments[number];
export type Comment = {
  comment_id: string; video_id: string; text: string; published_at: string; collected_at: string;
  sentiment: Sentiment | null; confidence: number | null; analysed_at: string | null;
  model_version: string | null; status: string; quality_flags: string[]; reason: string;
  period: "Historical" | "Monitoring period" | "After monitoring" | "Unknown";
};
export type Row = Record<string, string>;
export function csv(text: string, required: string[] = []): Row[] {
  const rows = parse(text.replace(/^\uFEFF/, ""), { columns: true, skip_empty_lines: true, bom: true }) as Row[];
  // Validate headers even for a header-only CSV.
  const header = parse(text.replace(/^\uFEFF/, ""), { to_line: 1, bom: true })[0] as string[] | undefined;
  if (required.some(key => !header?.includes(key))) throw new Error("Dataset has missing required columns.");
  return rows;
}
export function validDate(value: unknown): string | null {
  if (typeof value !== "string" || !value.trim()) return null;
  const time = Date.parse(value);
  return Number.isFinite(time) ? new Date(time).toISOString() : null;
}
export function latest(values: (string | null)[]) {
  return values.reduce<string | null>((best, value) => value && (!best || value > best) ? value : best, null);
}
export function combine(comments: Row[], predictions: Row[], statuses: Row[], started: string | null) {
  let invalidPredictions = 0;
  let duplicateComments = 0;
  let malformedComments = 0;
  const resultMap = new Map<string, Row>();
  for (const prediction of predictions) {
    const value = Number(prediction.confidence);
    if (!prediction.comment_id || !sentiments.includes(prediction.sentiment as Sentiment) ||
        !prediction.confidence?.trim() || !Number.isFinite(value) || value < 0 || value > 1 ||
        !validDate(prediction.analysed_at) || !prediction.model_version) { invalidPredictions++; continue; }
    const previous = resultMap.get(prediction.comment_id);
    if (!previous || validDate(prediction.analysed_at)! > validDate(previous.analysed_at)!) resultMap.set(prediction.comment_id, prediction);
  }
  const statusMap = new Map(statuses.map(row => [row.comment_id, row]));
  const seen = new Set<string>();
  const start = started ? Date.parse(started) : null;
  const merged: Comment[] = [];
  for (const row of comments) {
    const id = row.comment_id?.trim();
    if (!id) { malformedComments++; continue; }
    if (seen.has(id)) { duplicateComments++; continue; }
    seen.add(id);
    const publication = validDate(row.published_at);
    const collection = validDate(row.collected_at);
    const malformed = !publication || !collection || !row.video_id?.trim();
    if (malformed) malformedComments++;
    const prediction = resultMap.get(id);
    const status = statusMap.get(id);
    const time = publication ? Date.parse(publication) : null;
    const period = start === null || time === null ? "Unknown" : time < start ? "Historical" : time < start + 48 * 3600000 ? "Monitoring period" : "After monitoring";
    merged.push({ comment_id: id, video_id: row.video_id || "", text: row.text || "", published_at: publication || "", collected_at: collection || "",
      sentiment: prediction?.sentiment as Sentiment || null, confidence: prediction ? Number(prediction.confidence) : null,
      analysed_at: validDate(prediction?.analysed_at), model_version: prediction?.model_version || null,
      status: malformed ? "malformed" : prediction ? "analysed" : status?.status || "awaiting_analysis", reason: status?.reason || (malformed ? "Invalid source metadata" : ""),
      quality_flags: [...(status?.quality_flags?.split(";").filter(Boolean) || ["relevance_not_verified"]), ...(malformed ? ["invalid_timestamp_or_video_id"] : [])], period });
  }
  return { comments: merged, quality: { invalidPredictions, duplicateComments, malformedComments } };
}
export function stats(comments: Comment[]) {
  const counts = { Positive: 0, Neutral: 0, Negative: 0 };
  let unprocessable = 0;
  for (const row of comments) {
    if (row.sentiment) counts[row.sentiment]++;
    else if (["empty", "malformed", "unsupported_language", "inference_failed"].includes(row.status)) unprocessable++;
  }
  const analysed = counts.Positive + counts.Neutral + counts.Negative;
  return { collected: comments.length, analysed, awaiting: comments.length - analysed, unprocessable, counts,
    percentages: Object.fromEntries(sentiments.map(label => [label, analysed ? counts[label] / analysed * 100 : null])) as Record<Sentiment, number | null>,
    score: analysed ? (counts.Positive - counts.Negative) / analysed * 100 : null,
    lastCollection: latest(comments.map(row => validDate(row.collected_at))), lastAnalysis: latest(comments.map(row => row.analysed_at)) };
}
export type Filters = { search: string; from: string; to: string; sentiment: string; period: string; bucket?: string; grouping: "hour" | "day" };
export function bucket(date: string, grouping: "hour" | "day") { return date.slice(0, grouping === "day" ? 10 : 13); }
export function filterComments(comments: Comment[], filter: Filters) {
  const term = filter.search.toLowerCase();
  return comments.filter(row => (!term || row.text.toLowerCase().includes(term) || row.video_id.toLowerCase().includes(term)) &&
    (!filter.from || row.published_at.slice(0, 10) >= filter.from) && (!filter.to || (row.published_at && row.published_at.slice(0, 10) <= filter.to)) &&
    (!filter.sentiment || (filter.sentiment === "Unprocessed" ? !row.sentiment : row.sentiment === filter.sentiment)) &&
    (!filter.period || row.period === filter.period) && (!filter.bucket || bucket(row.published_at, filter.grouping) === filter.bucket));
}
export function trend(comments: Comment[], grouping: "hour" | "day") {
  const groups = new Map<string, { time: string; Positive: number; Neutral: number; Negative: number; total: number }>();
  for (const row of comments) {
    if (!row.sentiment || !row.published_at) continue;
    const time = bucket(row.published_at, grouping);
    const group = groups.get(time) || { time, Positive: 0, Neutral: 0, Negative: 0, total: 0 };
    group[row.sentiment]++; group.total++; groups.set(time, group);
  }
  return [...groups.values()].sort((a, b) => a.time.localeCompare(b.time)).map(group => ({ ...group,
    PositivePercent: group.Positive / group.total * 100, NeutralPercent: group.Neutral / group.total * 100, NegativePercent: group.Negative / group.total * 100 }));
}
