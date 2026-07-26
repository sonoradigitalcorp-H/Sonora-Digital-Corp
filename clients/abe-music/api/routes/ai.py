import subprocess
import os
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from routes.auth import verify_token

router = APIRouter(prefix="/api", tags=["ai"])

class AIRequest(BaseModel):
    question: str
    context: str = ""

@router.post("/ai/ask")
def ask_ai(req: AIRequest, _=Depends(verify_token)):
    system = "Eres el asistente de ABE Music Group, un sello discográfico y plataforma de servicios para músicos. Responde en español de forma clara y profesional. Sé conciso."
    if req.context:
        system += f"\n\nContexto: {req.context}"
    prompt = f"{system}\n\nPregunta: {req.question}"

    try:
        result = subprocess.run(
            ["opencode", "run", prompt, "--model", "opencode/deepseek-v4-flash-free", "--pure"],
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        clean = ansi_escape.sub('', output)
        lines = [l.strip() for l in clean.split('\n') if l.strip() and not l.startswith('>') and 'build ·' not in l]
        answer = lines[-1] if lines else "No pude procesar tu consulta."
    except subprocess.TimeoutExpired:
        answer = "La consulta tardó demasiado. Intenta de nuevo."
    except Exception as e:
        answer = f"Error al procesar la consulta."

    return {"answer": answer}
