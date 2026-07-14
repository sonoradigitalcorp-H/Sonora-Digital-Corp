import { NextRequest, NextResponse } from "next/server";

const MCP = "http://127.0.0.1:8180/mcp/execute";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const topic = body.topic || body.type;
    const id = body.data?.id || body.id;

    if (topic && id) {
      await fetch(MCP, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "mp_handle_webhook",
          args: { topic, id },
        }),
        signal: AbortSignal.timeout(15000),
      });
    }

    return NextResponse.json({ received: true });
  } catch {
    return NextResponse.json({ received: true });
  }
}

export async function GET() {
  return NextResponse.json({ ok: true, message: "MercadoPago webhook endpoint" });
}
