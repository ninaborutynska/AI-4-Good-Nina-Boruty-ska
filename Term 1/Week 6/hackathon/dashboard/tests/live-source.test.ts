import { afterEach, describe, expect, it, vi } from "vitest";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import path from "node:path";
vi.mock("server-only", () => ({}));
let directory = "";
afterEach(async () => { vi.unstubAllEnvs(); vi.restoreAllMocks(); if (directory) await rm(directory, { recursive: true, force: true }); });
describe("Live snapshot synchronization", () => {
  it("loads an atomic generation and marks preserved data stale when the bridge stops", async () => {
    vi.resetModules();
    directory = await mkdtemp(path.join(process.cwd(), "tests/.live-test-"));
    await writeFile(path.join(directory, "youtube_comments.csv"), "comment_id,video_id,text,published_at,collected_at\na,video,Synthetic fixture,2026-10-14T00:00:00Z,2026-10-14T01:00:00Z\n");
    await writeFile(path.join(directory, "current.json"), JSON.stringify({ data_directory: directory, commit: "a".repeat(40) }));
    await writeFile(path.join(directory, "status.json"), JSON.stringify({ ok: true, checked_at: new Date().toISOString() }));
    vi.stubEnv("DATA_SOURCE", "local"); vi.stubEnv("LIVE_SYNC_DIR", directory);
    const { getData } = await import("../lib/source");
    const first = await getData();
    expect(first.error).toBeNull(); expect(first.snapshot?.overview.collected).toBe(1);
    expect(first.snapshot?.source).toBe("Live GitHub synchronization"); expect(first.snapshot?.lastSync).toBeTruthy();
    await writeFile(path.join(directory, "status.json"), JSON.stringify({ ok: true, checked_at: "2000-01-01T00:00:00Z" }));
    const future = Date.now() + 61000; vi.spyOn(Date, "now").mockReturnValue(future);
    const stale = await getData();
    expect(stale.stale).toBe(true); expect(stale.error).toMatch(/stopped checking/);
    expect(stale.snapshot?.overview.collected).toBe(1);
  });
});
