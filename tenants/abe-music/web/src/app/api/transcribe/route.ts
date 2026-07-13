import { NextRequest, NextResponse } from "next/server";

export async function POST(req: NextRequest) {
  try {
    const formData = await req.formData();
    const audioFile = formData.get("audio") as File;
    if (!audioFile) {
      return NextResponse.json({ text: "" });
    }
    // TODO: Implement actual STT via Whisper or MCP
    // For now, return placeholder
    return NextResponse.json({ text: "Hola, ¿qué servicios tienen disponibles?" });
  } catch (err: any) {
    return NextResponse.json({ text: "" });
  }
}
