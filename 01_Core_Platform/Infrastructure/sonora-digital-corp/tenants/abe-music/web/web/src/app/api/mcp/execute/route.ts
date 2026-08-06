import { NextRequest, NextResponse } from "next/server";

const MCP_GATEWAY = "http://127.0.0.1:8180";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const resp = await fetch(`${MCP_GATEWAY}/mcp/execute`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30000),
    });
    const data = await resp.json();
    return NextResponse.json(data);
  } catch (err: any) {
    return NextResponse.json({ error: err.message }, { status: 500 });
  }
}
