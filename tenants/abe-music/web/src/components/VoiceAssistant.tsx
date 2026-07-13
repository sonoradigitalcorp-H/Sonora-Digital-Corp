"use client";

import { useState, useRef, useCallback, useEffect } from "react";

type Status = "idle" | "listening" | "processing" | "speaking" | "error";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export default function VoiceAssistant() {
  const [status, setStatus] = useState<Status>("idle");
  const [messages, setMessages] = useState<Message[]>([]);
  const [transcript, setTranscript] = useState("");
  const mediaRecorder = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);

  const startListening = useCallback(async () => {
    try {
      setStatus("listening");
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const recorder = new MediaRecorder(stream);
      mediaRecorder.current = recorder;
      audioChunks.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.current.push(e.data);
      };

      recorder.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const audioBlob = new Blob(audioChunks.current, { type: "audio/webm" });
        await processAudio(audioBlob);
      };

      recorder.start();
      setTimeout(() => {
        if (recorder.state === "recording") recorder.stop();
      }, 5000);
    } catch {
      setStatus("error");
    }
  }, []);

  const processAudio = async (audio: Blob) => {
    setStatus("processing");
    try {
      const formData = new FormData();
      formData.append("audio", audio, "input.webm");

      const sttResp = await fetch("/api/transcribe", {
        method: "POST",
        body: formData,
      });
      const sttData = await sttResp.json();
      const text = sttData.text || "";
      setTranscript(text);
      setMessages((prev) => [...prev, { role: "user", text }]);

      const mcpResp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "rag_search",
          args: { tenant_id: "abe_music", query: text },
        }),
      });
      const mcpData = await mcpResp.json();
      const context = mcpData?.result?.results
        ?.map((r: any) => r.payload?.content)
        .filter(Boolean)
        .join("\n") || "";

      const llmResp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "llm_chat",
          args: {
            system: `Eres un asistente de ABE Music. Usa este contexto para responder:\n${context}\nResponde en español, sé breve y amigable.`,
            message: text,
          },
        }),
      });
      const llmData = await llmResp.json();
      const reply = llmData?.result?.content || "Lo siento, no pude procesar tu solicitud.";
      setMessages((prev) => [...prev, { role: "assistant", text: reply }]);

      setStatus("speaking");
      const ttsResp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "omnivoice_speak",
          args: { text: reply, language: "es" },
        }),
      });
      const ttsData = await ttsResp.json();
      const audioUrl = ttsData?.result?.audio_url || ttsData?.result?.url;
      if (audioUrl) {
        const audioEl = new Audio(audioUrl);
        audioEl.onended = () => setStatus("idle");
        await audioEl.play();
      } else {
        setStatus("idle");
      }
    } catch {
      setStatus("error");
      setTimeout(() => setStatus("idle"), 2000);
    }
  };

  return (
    <div className="fixed bottom-4 right-4 z-50 flex flex-col items-end gap-2">
      {messages.length > 0 && (
        <div className="mb-2 max-h-60 w-80 overflow-y-auto rounded-lg bg-gray-900 p-3 text-sm text-white shadow-lg">
          {messages.map((m, i) => (
            <div key={i} className={`mb-1 ${m.role === "user" ? "text-right" : "text-left"}`}>
              <span className={`inline-block rounded px-2 py-1 ${m.role === "user" ? "bg-blue-600" : "bg-gray-700"}`}>
                {m.text.length > 80 ? m.text.slice(0, 80) + "..." : m.text}
              </span>
            </div>
          ))}
        </div>
      )}

      <button
        onClick={status === "listening" ? () => mediaRecorder.current?.stop() : startListening}
        disabled={status === "processing" || status === "speaking"}
        className={`flex h-14 w-14 items-center justify-center rounded-full text-white shadow-lg transition-all ${
          status === "listening" ? "animate-pulse bg-red-500" :
          status === "processing" ? "bg-yellow-500" :
          status === "speaking" ? "bg-green-500" :
          "bg-purple-600 hover:bg-purple-700"
        }`}
        title={
          status === "listening" ? "Toca para detener" :
          status === "processing" ? "Procesando..." :
          status === "speaking" ? "Hablando..." :
          "Pulsa para hablar"
        }
      >
        {status === "listening" ? (
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <rect x="6" y="4" width="4" height="16" rx="1" />
            <rect x="14" y="4" width="4" height="16" rx="1" />
          </svg>
        ) : (
          <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m-4 0h8m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
          </svg>
        )}
      </button>

      {transcript && status === "idle" && (
        <div className="w-80 rounded bg-gray-800 p-2 text-xs text-gray-400 shadow">
          "{transcript}"
        </div>
      )}
    </div>
  );
}
