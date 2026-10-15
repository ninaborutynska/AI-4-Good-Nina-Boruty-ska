import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
vi.mock("server-only", () => ({}));
const comments = 'comment_id,video_id,text,published_at,collected_at\na,video,Synthetic fixture,2026-10-14T00:00:00Z,2026-10-14T01:00:00Z\n';
let time = 100000;
beforeEach(() => { vi.resetModules(); vi.stubEnv("GITHUB_TOKEN", "synthetic-test-secret"); vi.stubEnv("DATA_SOURCE", "github"); vi.spyOn(Date, "now").mockImplementation(() => time); });
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals(); vi.restoreAllMocks(); });
function mockGithub() {
  return vi.fn(async (url: string) => url.includes("/commits/") ? new Response(JSON.stringify({sha:"a".repeat(40)})) : url.includes("youtube_comments.csv") ? new Response(comments) : new Response("", {status:404}));
}
describe("Server synchronization", () => {
  it("coalesces concurrent requests, caches for 60 seconds and checks unchanged commits cheaply", async () => {
    const fetch = mockGithub(); vi.stubGlobal("fetch", fetch);
    const { getData } = await import("../lib/source");
    const [first, second] = await Promise.all([getData(), getData()]);
    expect(first).toEqual(second); expect(first.snapshot?.overview.collected).toBe(1);
    expect(fetch).toHaveBeenCalledTimes(8);
    expect(fetch.mock.calls.slice(1).every(([url]) => url.includes("ref=" + "a".repeat(40)))).toBe(true);
    await getData(); expect(fetch).toHaveBeenCalledTimes(8);
    time += 61000; await getData(); expect(fetch).toHaveBeenCalledTimes(9);
    expect(JSON.stringify(first)).not.toContain("synthetic-test-secret");
  });
  it("preserves the last successful snapshot with a connection error on refresh failure", async () => {
    const fetch = mockGithub(); vi.stubGlobal("fetch", fetch);
    const { getData } = await import("../lib/source");
    const first = await getData();
    time += 61000; fetch.mockImplementation(async () => new Response("", {status:403}));
    const failed = await getData();
    expect(failed.stale).toBe(true); expect(failed.snapshot?.lastRefresh).toBe(first.snapshot?.lastRefresh);
    expect(failed.error).toMatch(/limit or permission/);
  });
  it("returns an error with no invented statistics when authentication is missing", async () => {
    vi.stubEnv("GITHUB_TOKEN", "");
    const { getData } = await import("../lib/source");
    const state = await getData(); expect(state.snapshot).toBeNull(); expect(state.error).toMatch(/GITHUB_TOKEN/);
  });
});
