import { NextRequest, NextResponse } from 'next/server';
import { generateResponse } from '@/lib/chat-knowledge';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { message, page, history } = body;

    if (!message || typeof message !== 'string') {
      return NextResponse.json(
        { error: 'Message is required' },
        { status: 400 }
      );
    }

    // Simulate processing delay for natural feel
    await new Promise(resolve => setTimeout(resolve, 300 + Math.random() * 400));

    const { response, suggestions } = generateResponse(
      message.trim(),
      page || '/dashboard'
    );

    return NextResponse.json({
      response,
      suggestions,
      timestamp: new Date().toISOString(),
    });
  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Failed to process message' },
      { status: 500 }
    );
  }
}
