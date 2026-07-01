import asyncio
import json
import logging

from ..core.abe_service import abe_service
from .middleware import verify_token

log = logging.getLogger("abe.ws")


async def handle_websocket(websocket):
    await websocket.accept()
    session_id = None
    user_info = {"role": "fan", "user_id": "anonymous"}

    try:
        while True:
            raw = await asyncio.wait_for(websocket.receive_text(), timeout=600)
            data = json.loads(raw)
            msg_type = data.get("type", "")

            if msg_type == "auth":
                token = data.get("token", "")
                payload = verify_token(token)
                if payload:
                    user_info = {"role": payload.role.value, "user_id": payload.sub}
                    await websocket.send_json({"type": "auth_ok", "role": payload.role.value})
                else:
                    await websocket.send_json({"type": "auth_error", "error": "Invalid token"})
                continue

            if msg_type == "chat":
                text = data.get("text", "")
                result = await abe_service.chat.process(
                    text,
                    session_id=data.get("session_id"),
                    context={"role": user_info["role"], "user_id": user_info["user_id"]},
                )
                session_id = result.get("session_id", session_id)
                await websocket.send_json({
                    "type": "chat_response",
                    **result,
                })
                continue

            if msg_type == "audio_chunk":
                result = await abe_service.voice.process_chunk(
                    data.get("audio", ""),
                    session_id=data.get("session_id", session_id),
                    final=data.get("final", False),
                )
                session_id = result.get("session_id", session_id)
                await websocket.send_json({
                    "type": "audio_response",
                    **result,
                })
                continue

            if msg_type == "ping":
                await websocket.send_json({"type": "pong"})
                continue

            await websocket.send_json({"type": "error", "error": f"Unknown type: {msg_type}"})

    except TimeoutError:
        log.info(f"WS timeout for {user_info}")
    except Exception as e:
        log.warning(f"WS error: {e}")
    finally:
        try:
            await websocket.close()
        except Exception:
            pass
