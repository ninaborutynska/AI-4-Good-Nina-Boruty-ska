import { getData } from "@/lib/source";
export const runtime = "nodejs";
export const dynamic = "force-dynamic";
export async function GET() {
  const state = await getData();
  return Response.json(state, { status: state.snapshot ? 200 : 503, headers: { "Cache-Control": "no-store" } });
}
