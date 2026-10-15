"use client";
import { useEffect, useState } from "react";
import type { Comment, stats, combine } from "@/lib/data";
export type Snapshot = {
  comments: Comment[]; overview: ReturnType<typeof stats>; quality: ReturnType<typeof combine>["quality"];
  monitoringStarted: string | null; monitoringEnds: string | null; lastRefresh: string; lastCollection: string | null;
  source: string; commit: string | null; evaluation: Record<string, unknown>;
  lastSync?: string | null;
};
export type DataState = { snapshot: Snapshot | null; error: string | null; stale: boolean; checkedAt: string };
export function useData() {
  const [state, setState] = useState<DataState | null>(null);
  useEffect(() => {
    let alive = true;
    let pending = false;
    const controller = new AbortController();
    const refresh = async () => {
      if (pending) return;
      pending = true;
      try {
        const response = await fetch("/api/data", { cache: "no-store", signal: controller.signal });
        const data = await response.json() as DataState;
        if (alive) setState(data);
      } catch {
        if (alive) setState(previous => ({ snapshot: previous?.snapshot || null, stale: !!previous?.snapshot, error: "Could not connect to the dashboard data server. Retrying in 60 seconds.", checkedAt: new Date().toISOString() }));
      } finally { pending = false; }
    };
    void refresh();
    const timer = setInterval(() => { void refresh(); }, 60000);
    return () => { alive = false; controller.abort(); clearInterval(timer); };
  }, []);
  return state;
}
export function formatDate(value: string | null | undefined) {
  return value ? new Date(value).toLocaleString("en-GB", { timeZone: "UTC" }) + " UTC" : "Unavailable";
}
