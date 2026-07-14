"use client";
import { useState, useCallback, useRef } from "react";

type VoiceStatus = "idle" | "listening" | "processing" | "speaking" | "error";

interface VoiceOptions {
  tenant?: string;
  voice?: string;
  language?: string;
  onResult?: (text: string, response: string) => void;
}

export function useVoice(opts: VoiceOptions = {}) {
  const [status, setStatus] = useState<VoiceStatus>("idle");
  const [transcript, setTranscript] = useState("");
  const [response, setResponse] = useState("");
  const recognitionRef = useRef<any>(null);

  const speak = useCallback(async (text: string) => {
    setStatus("speaking");
    try {
      const resp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "omnivoice_speak",
          args: { text, voice: opts.voice || "default", language: opts.language || "es" },
        }),
      });
      const data = await resp.json();
      const audioUrl = data?.result?.audio_url || data?.result?.url;
      if (audioUrl) {
        const audio = new Audio(audioUrl);
        await audio.play();
      }
    } catch {
      setStatus("error");
    }
    setStatus("idle");
  }, [opts.voice, opts.language]);

  const listen = useCallback(async (): Promise<string> => {
    return new Promise((resolve) => {
      const SR = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
      if (!SR) { resolve(""); return; }
      const r = new SR();
      r.lang = "es-MX";
      r.interimResults = false;
      r.onstart = () => setStatus("listening");
      r.onresult = (e: any) => {
        const text = e.results[0][0].transcript;
        setTranscript(text);
        setStatus("processing");
        resolve(text);
      };
      r.onerror = () => { setStatus("error"); resolve(""); };
      r.onend = () => { setStatus("idle"); recognitionRef.current = null; };
      recognitionRef.current = r;
      r.start();
    });
  }, []);

  const ask = useCallback(async (question: string, context?: string) => {
    setStatus("processing");
    setTranscript(question);
    try {
      const resp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "llm_chat",
          args: {
            system: context
              ? `Eres un asistente de ${opts.tenant || "SDC"}. Usa este contexto:\n${context}\nResponde en español, sé breve.`
              : `Eres un asistente de ${opts.tenant || "SDC"}. Responde en español, sé breve.`,
            message: question,
          },
        }),
      });
      const data = await resp.json();
      const answer = data?.result?.content || "Lo siento, no pude procesar tu solicitud.";
      setResponse(answer);
      opts.onResult?.(question, answer);
      setStatus("idle");
      return answer;
    } catch {
      setStatus("error");
      return "Error al procesar";
    }
  }, [opts.tenant, opts.onResult]);

  const listenAndAsk = useCallback(async (context?: string) => {
    const question = await listen();
    if (question) return ask(question, context);
    return "";
  }, [listen, ask]);

  const stopListening = useCallback(() => {
    recognitionRef.current?.stop();
    setStatus("idle");
  }, []);

  return { status, transcript, response, speak, listen, ask, listenAndAsk, stopListening };
}
