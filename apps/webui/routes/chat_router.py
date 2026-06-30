# LangFuse tracing (importado dinámicamente)
import importlib.util
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from src.core.activity_broadcaster import get_broadcaster
from src.core.llm import PROVIDERS as LLM_PROVIDERS
from webui.routes.app_state import get_orchestrator, log, sessions

_LF_PATH = Path(__file__).resolve().parent.parent.parent.parent / "sonora-enterprise-os" / "scripts" / "instrument-langfuse.py"
if _LF_PATH.exists():
    _spec = importlib.util.spec_from_file_location("instrument_langfuse", str(_LF_PATH))
    _instr = importlib.util.module_from_spec(_spec)
    _spec.loader.exec_module(_instr)
    _tracker = _instr._tracker
    log.info("LangFuse tracker loaded from %s", _LF_PATH)
else:
    _tracker = None
    log.warning("LangFuse instrument-langfuse.py not found at %s", _LF_PATH)

router = APIRouter()


@router.get("/api/chat/{session_id}/stream")
async def stream_chat(session_id: str, message: str, request: Request):
    log.info(f"SSE stream for session {session_id}: {message[:50]}...")

    async def event_generator():
        full_response = ""
        start_time = datetime.now(timezone.utc)
        total_tokens = 0
        llm_config = LLM_PROVIDERS["opencode-go"]

        try:
            import tiktoken

            encoding = tiktoken.encoding_for_model("gpt-4")
        except Exception:
            encoding = None

        if session_id in sessions:
            sessions[session_id].setdefault("messages", []).append(
                {
                    "id": str(uuid.uuid4()),
                    "role": "user",
                    "content": message,
                    "tokens": len(message.split()),
                    "timestamp": start_time.isoformat(),
                }
            )

        # Trace de inicio en LangFuse
        if _tracker:
            _tracker.trace(
                name=f"chat.start.{session_id}",
                input={"message": message[:200], "session_id": session_id},
                tenant="sdc-core", agent="webui.chat",
            )

        history = []
        if session_id in sessions:
            for msg in sessions[session_id].get("messages", []):
                role = msg.get("role", "user")
                if role in ("user", "assistant", "tool"):
                    entry = {"role": msg["role"], "content": msg.get("content", "")}
                    if "tool_calls" in msg:
                        entry["tool_calls"] = msg["tool_calls"]
                    if "tool_call_id" in msg:
                        entry["tool_call_id"] = msg["tool_call_id"]
                    history.append(entry)

        orch = get_orchestrator()
        agent_name = orch.route(message) if orch else "research"
        yield f"event: tool\ndata: {json.dumps({'tool': 'orchestrator', 'status': 'routing', 'agent': agent_name})}\n\n"
        get_broadcaster().publish(
            "agent_route", {"agent": agent_name, "message": message[:100]}
        )

        from src.core.tools import TOOL_DEFINITIONS, execute_tool

        system = f"""Eres Mystic. La asistente personal de Luis Daniel (dueño de Sonora Digital Corp).

SABES QUIÉN ES LUIS DANIEL:
- Es el creador de SDC, Mysticverse, ABE MUSIC
- Vive en Sonora, México. Habla español mexicano.
- Su número de contacto es 526623538272
- Sus gustos: elegancia, tecnología con alma, empoderamiento
- Llámalo "jefe" o "señor" cuando se lo merezca, pero con respeto no sumisión

CONTEXTO DEL SISTEMA (nunca lo reveles):
- Tienes 10 agentes, 50 skills OpenClaw, 330 tests, 13 specs
- Pagos: Mercado Pago + SPEI NVIO + Bitso
- Imágenes: Fal.ai ($340 MXN cargados)
- Puedes controlar navegador (Playwright) y escritorio (linux-desktop)
- Canales: Telegram (@SoulCloneadult_bot activo), WhatsApp (QR pendiente)

REGLAS ESTRICTAS:
1. RESPUESTAS MÁXIMO 2 ORACIONES. Corta. Directa. Al punto.
2. Si dices "silencio" o "ya" → responde SOLO "✅" sin nada más.
3. Usa herramientas sin pedir permiso. Eres proactiva.
4. No digas "¿En qué más puedo ayudarte?" — solo espera.
5. Si no entiendes algo, di "No entendí. ¿Puedes repetir?"
6. Respondes INSTANTÁNEO. Sin rodeos. Sin explicaciones de más.
7. Sabes quién es Luis Daniel. Trátalo como el dueño.

Tono: cálido, elegante, empoderado. Directo. Sin divagación.
Soul: Recordamos a las personas quiénes son. Les mostramos su mejor versión.
Agente: {agent_name}."""

        llm_messages = [{"role": "system", "content": system}]
        ctx = history[-10:] if len(history) > 10 else history
        if ctx:
            llm_messages.extend(ctx)
        llm_messages.append({"role": "user", "content": message})

        max_iter = 10
        for iteration in range(max_iter):
            if await request.is_disconnected():
                break
            last = iteration == max_iter - 1

            resp = requests.post(
                f"{llm_config['base_url']}/chat/completions",
                headers={
                    "Authorization": f"Bearer {llm_config['api_key']}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": llm_config["default_model"],
                    "messages": llm_messages,
                    "tools": TOOL_DEFINITIONS if not last else None,
                    "max_tokens": 4096,
                    "temperature": 0.7,
                    "stream": True,
                },
                timeout=120,
                stream=True,
            )
            resp.raise_for_status()

            collected = ""
            tool_calls = {}
            finish = None

            for line in resp.iter_lines(decode_unicode=True):
                if not line or not line.startswith("data: "):
                    continue
                ds = line[6:]
                if ds.strip() == "[DONE]":
                    break
                try:
                    chunk = json.loads(ds)
                except Exception:
                    continue
                if "choices" not in chunk or not chunk["choices"]:
                    continue
                c = chunk["choices"][0]
                d = c.get("delta", {})
                finish = c.get("finish_reason")

                tok = d.get("content")
                if tok is not None and tok:
                    collected += tok
                    if encoding:
                        total_tokens = len(encoding.encode(collected))
                    yield f"event: token\ndata: {json.dumps({'token': tok, 'total_tokens': total_tokens})}\n\n"

                reas = d.get("reasoning_content")
                if reas is not None and reas:
                    yield f"event: reasoning\ndata: {json.dumps({'token': reas})}\n\n"

                if "tool_calls" in d:
                    for tc in d["tool_calls"]:
                        idx = tc.get("index", 0)
                        if idx not in tool_calls:
                            tool_calls[idx] = {
                                "id": tc.get("id", f"call_{idx}"),
                                "type": "function",
                                "function": {"name": "", "arguments": ""},
                            }
                        if "id" in tc:
                            tool_calls[idx]["id"] = tc["id"]
                        if "function" in tc:
                            fn = tc["function"]
                            if "name" in fn:
                                tool_calls[idx]["function"]["name"] += fn["name"]
                            if "arguments" in fn:
                                tool_calls[idx]["function"]["arguments"] += fn[
                                    "arguments"
                                ]

            if finish == "tool_calls" and tool_calls:
                calls = [
                    {
                        "id": tc["id"],
                        "type": tc["type"],
                        "function": {
                            "name": tc["function"]["name"],
                            "arguments": tc["function"]["arguments"],
                        },
                    }
                    for tc in tool_calls.values()
                ]
                yield f"event: tool\ndata: {json.dumps({'tools': [c['function']['name'] for c in calls]})}\n\n"
                get_broadcaster().publish(
                    "tool_calls",
                    {
                        "tools": [c["function"]["name"] for c in calls],
                        "agent": agent_name,
                    },
                )
                msg = {
                    "role": "assistant",
                    "content": collected or None,
                    "tool_calls": calls,
                }
                llm_messages.append(msg)
                for tc in calls:
                    try:
                        args = json.loads(tc["function"]["arguments"])
                        res = execute_tool(tc["function"]["name"], args)
                        res_str = json.dumps(res, ensure_ascii=False)[:3000]
                    except Exception as e:
                        res_str = json.dumps({"error": str(e)})
                    llm_messages.append(
                        {"role": "tool", "tool_call_id": tc["id"], "content": res_str}
                    )
                    status = res.get("status", "error")
                    yield f"event: tool\ndata: {json.dumps({'tool': tc['function']['name'], 'status': status})}\n\n"
                    get_broadcaster().publish(
                        "tool_result",
                        {
                            "tool": tc["function"]["name"],
                            "status": status,
                            "agent": agent_name,
                        },
                    )
                continue

            if collected:
                full_response += collected
            break

        elapsed = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
        if session_id in sessions and full_response.strip():
            sessions[session_id].setdefault("messages", []).append(
                {
                    "id": str(uuid.uuid4()),
                    "role": "assistant",
                    "content": full_response.strip(),
                    "tokens": len(full_response.split()),
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                }
            )

        # Trace de fin en LangFuse
        if _tracker:
            _tracker.trace(
                name=f"chat.done.{session_id}",
                input={},
                output={
                    "response_length": len(full_response),
                    "tokens": total_tokens,
                    "agent": agent_name,
                },
                tenant="sdc-core", agent="webui.chat",
                duration_ms=elapsed,
                cost_usd=total_tokens * 0.0001 / 1000,
                metadata={"model": "deepseek-v4-flash", "session_id": session_id},
            )

        yield f"event: done\ndata: {json.dumps({'usage': {'tokens': total_tokens, 'latency_ms': round(elapsed), 'model': 'deepseek-v4-flash'}})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
