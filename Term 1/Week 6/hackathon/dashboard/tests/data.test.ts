import { describe, expect, it } from "vitest";
import { combine, csv, stats, trend, filterComments } from "../lib/data";
const source = (id: string, publication = "2026-10-14T01:00:00Z") => ({ comment_id: id, video_id: "test-video", text: "Synthetic fixture", published_at: publication, collected_at: "2026-10-14T02:00:00Z" });
const prediction = (id: string, sentiment = "Positive", confidence = "0.8") => ({ comment_id: id, sentiment, confidence, model_version: "test-double", analysed_at: "2026-10-14T03:00:00Z" });
describe("Real-data transformations (synthetic test fixtures only)", () => {
  it("joins by comment ID and excludes duplicates and orphan predictions", () => {
    const result = combine([source("a"), source("a"), source("b")], [prediction("a"), prediction("orphan")], [], null);
    expect(result.comments).toHaveLength(2);
    expect(result.quality.duplicateComments).toBe(1);
    expect(stats(result.comments)).toMatchObject({ collected: 2, analysed: 1, awaiting: 1, counts: { Positive: 1, Neutral: 0, Negative: 0 }, score: 100 });
  });
  it("shows unavailable percentages when there are no predictions", () => {
    expect(stats(combine([source("a")], [], [], null).comments).percentages.Positive).toBeNull();
    expect(stats([]).score).toBeNull();
  });
  it("rejects empty, nonfinite and out-of-range confidence", () => {
    const result = combine([source("a"), source("b"), source("c")], [prediction("a", "Positive", ""), prediction("b", "Neutral", "NaN"), prediction("c", "Negative", "1.1")], [], null);
    expect(result.quality.invalidPredictions).toBe(3);
    expect(stats(result.comments).analysed).toBe(0);
  });
  it("distinguishes publication before, during and after the monitoring window", () => {
    const result = combine([source("a", "2026-10-13T23:59:59Z"), source("b", "2026-10-14T00:00:00Z"), source("c", "2026-10-16T00:00:00Z")], [], [], "2026-10-14T00:00:00Z");
    expect(result.comments.map(row => row.period)).toEqual(["Historical", "Monitoring period", "After monitoring"]);
  });
  it("groups by publication timestamp, using only classified comments", () => {
    const result = combine([source("a", "2020-01-01T01:00:00Z"), source("b", "2020-01-01T01:30:00Z"), source("c")], [prediction("a"), prediction("b", "Negative")], [], null);
    expect(trend(result.comments, "hour")).toEqual([{ time: "2020-01-01T01", total: 2, Positive: 1, Neutral: 0, Negative: 1, PositivePercent: 50, NeutralPercent: 0, NegativePercent: 50 }]);
  });
  it("filters comments behind a selected time bucket", () => {
    const rows = combine([source("a"), source("b", "2026-10-13T02:00:00Z")], [prediction("a")], [], null).comments;
    expect(filterComments(rows, { search: "fixture", from: "2026-10-14", to: "2026-10-14", sentiment: "Positive", period: "", grouping: "hour", bucket: "2026-10-14T01" }).map(row => row.comment_id)).toEqual(["a"]);
  });
  it("parses quoted multiline comments and validates headers", () => {
    expect(csv('comment_id,text\r\na,"first, line\nsecond line"\r\n', ["comment_id", "text"])[0].text).toBe("first, line\nsecond line");
    expect(() => csv("comment_id,text\na,x", ["published_at"])).toThrow();
  });
  it("keeps skipped records separate from successful sentiment totals", () => {
    const result = combine([source("a"), source("b")], [prediction("a", "Negative")], [{comment_id:"b",status:"unsupported_language",reason:"English model"}], null);
    expect(stats(result.comments)).toMatchObject({ analysed: 1, awaiting: 1, unprocessable: 1, score: -100 });
  });
});
