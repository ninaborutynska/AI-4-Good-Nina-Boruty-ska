import { afterEach, beforeEach, expect, it, vi } from "vitest";
import { mkdtemp, writeFile, rm } from "node:fs/promises";
import path from "node:path";
vi.mock("server-only", () => ({}));
const { spawn } = vi.hoisted(() => ({ spawn: vi.fn(() => ({ on: vi.fn(), unref: vi.fn() })) }));
vi.mock("node:child_process", () => ({ spawn }));
let directory = "";
beforeEach(async () => {
  vi.resetModules(); spawn.mockClear();
  directory = await mkdtemp(path.join(process.cwd(), "tests/.connection-test-"));
  vi.stubEnv("LIVE_SYNC_DIR", directory); vi.stubEnv("GITHUB_TOKEN", ""); vi.stubEnv("GITHUB_TOKEN_FILE", "");
  await writeFile(path.join(directory, "github-token"), "synthetic-saved-secret");
});
afterEach(async () => { vi.unstubAllEnvs(); vi.restoreAllMocks(); await rm(directory, { recursive: true, force: true }); });
it("keeps saved credentials configured during a transient failure without returning the secret", async () => {
  await writeFile(path.join(directory, "status.json"), JSON.stringify({ ok: false, checked_at: new Date().toISOString(), error: "Temporary download failure" }));
  const { ensureLiveSync } = await import("../lib/live-sync");
  const status = await ensureLiveSync();
  expect(status.configured).toBe(true); expect(status.state).toBe("retrying");
  expect(JSON.stringify(status)).not.toContain("synthetic-saved-secret"); expect(spawn).not.toHaveBeenCalled();
});
it("restarts a stale bridge using persisted credentials once, without passing the key in process arguments", async () => {
  await writeFile(path.join(directory, "status.json"), JSON.stringify({ ok: true, checked_at: "2000-01-01T00:00:00Z" }));
  const { ensureLiveSync } = await import("../lib/live-sync");
  expect((await ensureLiveSync()).state).toBe("starting"); await ensureLiveSync();
  expect(spawn).toHaveBeenCalledTimes(1);
  expect(JSON.stringify(spawn.mock.calls)).not.toContain("synthetic-saved-secret");
});
it("distinguishes a rejected saved key from a missing key", async () => {
  await writeFile(path.join(directory, "status.json"), JSON.stringify({ ok: false, checked_at: new Date().toISOString(), error: "GitHub authentication failed. Replace the token on the Connection page." }));
  const { connectionStatus } = await import("../lib/live-sync");
  expect(await connectionStatus()).toMatchObject({ configured: true, state: "invalid_credentials" });
  await rm(path.join(directory, "github-token"));
  expect(await connectionStatus()).toMatchObject({ configured: false, state: "not_configured" });
});
