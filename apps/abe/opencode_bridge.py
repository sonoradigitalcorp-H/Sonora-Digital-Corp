"""
Bridge between ABE Service and OpenCode.
Each user gets a persistent OpenCode session via the mystic agent.
"""
import asyncio
import json
import logging
import os
import subprocess
import time
import uuid

log = logging.getLogger("abe.opencode")

OPENCODE_CMD = os.path.expanduser("~/.local/bin/opencode")
PROJECT_DIR = os.path.expanduser("~/sonora-platform")


class OpenCodeBridge:
    def __init__(self):
        self._sessions: dict[str, dict] = {}
        self._lock = asyncio.Lock()

    async def process(
        self, text: str, session_id: str | None = None,
        context: dict | None = None,
    ) -> dict:
        if not session_id:
            session_id = f"oc_{uuid.uuid4().hex[:12]}"

        async with self._lock:
            session = self._sessions.get(session_id)
            is_new = session is None

            if is_new:
                self._sessions[session_id] = {"created": time.time()}
                opencode_session = None
            else:
                opencode_session = session.get("opencode_session")

            # Build prompt with RAG context if available
            rag_context = (context or {}).get("rag_context", [])
            enriched_text = text
            if rag_context:
                ctx_str = "\n".join(
                    f"- [{r.get('collection','?')}] {r.get('text','')[:500]}"
                    for r in rag_context[:5]
                )
                enriched_text = (
                    f"Contexto del negocio:\n{ctx_str}\n\n"
                    f"Pregunta del usuario: {text}"
                )

            cmd = [
                OPENCODE_CMD, "run",
                "--agent", "mystic",
                "--dir", PROJECT_DIR,
            ]

            if opencode_session:
                cmd.extend(["--continue", "--session", opencode_session])

            cmd.append(enriched_text)

            log.info(f"Running OpenCode: {' '.join(cmd[-4:])}")

            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120,
                    env={
                        **os.environ,
                        "OPENCODE_PERMISSION": json.dumps({"*": "allow"}),
                        "OPENCODE_DISABLE_AUTOUPDATE": "1",
                    },
                )

                stdout = result.stdout.strip()
                stderr = result.stderr.strip()

                # Parse the response
                response_text = ""
                if stdout:
                    response_text = stdout
                elif stderr:
                    response_text = stderr.split("\n")[-1] if stderr else ""

                if not response_text:
                    response_text = "Entendido. ¿En qué más puedo ayudarte?"

                if result.returncode != 0 and not response_text:
                    response_text = "Estoy procesando tu solicitud. Un momento por favor."

                # Extract session ID from output for continuation
                if is_new:
                    for line in stderr.split("\n"):
                        if "session" in line.lower():
                            import re
                            m = re.search(r'[a-f0-9]{8,}', line)
                            if m:
                                self._sessions[session_id]["opencode_session"] = m.group()
                                break

            except subprocess.TimeoutExpired:
                response_text = "La consulta tomó demasiado tiempo. Intenta de nuevo."
                log.warning("OpenCode timeout")
            except Exception as e:
                response_text = "Error al procesar tu mensaje."
                log.error(f"OpenCode error: {e}")

            return {
                "text": response_text,
                "session_id": session_id,
                "source": "opencode",
            }


# Singleton
bridge = OpenCodeBridge()
