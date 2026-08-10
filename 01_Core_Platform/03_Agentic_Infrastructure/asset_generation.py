#!/usr/bin/env python3
"""asset_generation.py — Generación de assets con prompts evaluados.

Prompts versionados: cada prompt tiene versión, score de calidad, feedback.
Solo genera cuando el usuario lo pide explícitamente.
Tipos: imagen, video, mockup, audio.
"""

import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


ASSETS_DIR = Path(__file__).parent / "asset_prompts"
ASSETS_DIR.mkdir(exist_ok=True)


@dataclass
class AssetPrompt:
    """Prompt versionado con score y feedback."""
    id: str
    tipo: str  # imagen, video, mockup, audio
    version: str
    prompt_template: str
    provider: str  # midjourney, runway, elevenlabs, figma
    score: float = 0.0  # 0-100, promedio de evaluaciones
    evaluaciones: int = 0
    feedback: list[str] = field(default_factory=list)
    parametros_recomendados: dict = field(default_factory=dict)
    casos_uso: list[str] = field(default_factory=list)
    creado_en: str = ""
    actualizado_en: str = ""


# Prompts base evaluados para Aztrotech
PROMPTS_EVALUADOS = {
    # --- IMÁGENES ---
    "img_empleado_digital_whatsapp": AssetPrompt(
        id="img_empleado_digital_whatsapp",
        tipo="imagen",
        version="1.0",
        prompt_template=(
            "A professional AI chatbot interface on a smartphone screen showing a conversation "
            "in Spanish, dark mode, clean modern design, WhatsApp-style, blue accents (#00d4ff), "
            "showing an automated response from a business assistant, holographic AI brain overlay, "
            "cinematic lighting, ultra realistic, 8k --ar 16:9 --style raw --q 2 --stylize 750"
        ),
        provider="midjourney",
        score=85.0,
        evaluaciones=3,
        casos_uso=["redes_sociales", "landing", "pitch"],
        parametros_recomendados={"ar": "16:9", "style": "raw", "q": 2, "stylize": 750},
    ),
    "img_empleado_digital_3d": AssetPrompt(
        id="img_empleado_digital_3d",
        tipo="imagen",
        version="1.0",
        prompt_template=(
            "A futuristic 3D render of an AI employee working in a modern office, "
            "holographic screens, data flowing, dark background with blue and purple accents, "
            "corporate technology aesthetic, no text, cinematic composition, 4k --ar 16:9 --style raw"
        ),
        provider="midjourney",
        score=80.0,
        evaluaciones=2,
        casos_uso=["presentaciones", "demo"],
    ),
    "img_mockup_plataforma": AssetPrompt(
        id="img_mockup_plataforma",
        tipo="imagen",
        version="1.0",
        prompt_template=(
            "A modern CRM dashboard mockup on a laptop screen, dark theme, "
            "showing customer data, charts, AI insights sidebar, professional UI/UX, "
            "clean typography, subtle animations, corporate colors blue/purple, "
            "photorealistic mockup, 8k --ar 16:9 --style raw"
        ),
        provider="midjourney",
        score=82.0,
        evaluaciones=2,
        casos_uso=["demo", "pitch", "redes_sociales"],
    ),
    "img_antes_despues": AssetPrompt(
        id="img_antes_despues",
        tipo="imagen",
        version="1.0",
        prompt_template=(
            "Split screen comparison: LEFT side shows chaos - paper documents, sticky notes, "
            "multiple phones ringing, stressed business owner. RIGHT side shows calm - one tablet "
            "with AI assistant handling everything, organized dashboard, happy owner. "
            "Before and after concept, professional photography, cinematic lighting --ar 16:9"
        ),
        provider="midjourney",
        score=88.0,
        evaluaciones=4,
        casos_uso=["redes_sociales", "landing", "presentaciones"],
    ),
    "img_caso_exito": AssetPrompt(
        id="img_caso_exito",
        tipo="imagen",
        version="1.0",
        prompt_template=(
            "A successful business owner shaking hands with an AI hologram in a modern warehouse, "
            "industrial setting, data visualizations floating in air, warm lighting, "
            "professional photography, success concept --ar 16:9 --style raw"
        ),
        provider="midjourney",
        score=78.0,
        evaluaciones=2,
        casos_uso=["testimonios", "casos_exito"],
    ),

    # --- VIDEOS ---
    "vid_empleado_digital_demo": AssetPrompt(
        id="vid_empleado_digital_demo",
        tipo="video",
        version="1.0",
        prompt_template=(
            "Cinematic shot of a smartphone screen showing an AI chatbot responding to customer messages "
            "in real-time, dark mode interface, blue accents, smooth camera movement, "
            "text appearing letter by letter, 10 seconds, professional tech aesthetic"
        ),
        provider="runway",
        score=75.0,
        evaluaciones=2,
        casos_uso=["landing", "presentaciones"],
        parametros_recomendados={"duration": 10, "ratio": "16:9", "motion": 80},
    ),
    "vid_plataforma_tour": AssetPrompt(
        id="vid_plataforma_tour",
        tipo="video",
        version="1.0",
        prompt_template=(
            "Smooth screen recording style video of a modern CRM dashboard, "
            "cursor clicking through features, charts animating, data flowing, "
            "professional UI transitions, 15 seconds, dark theme with blue accents"
        ),
        provider="runway",
        score=70.0,
        evaluaciones=1,
        casos_uso=["demo", "pitch"],
        parametros_recomendados={"duration": 15, "ratio": "16:9", "motion": 60},
    ),

    # --- MOCKUPS ---
    "mockup_mobile_app": AssetPrompt(
        id="mockup_mobile_app",
        tipo="mockup",
        version="1.0",
        prompt_template=(
            "iPhone 15 Pro mockup displaying a business AI assistant app, dark theme, "
            "chat interface with automated responses, blue accent color (#00d4ff), "
            "clean typography, professional UI, isometric view, white background"
        ),
        provider="figma",
        score=83.0,
        evaluaciones=3,
        casos_uso=["pitch", "redes_sociales"],
    ),
    "mockup_dashboard_web": AssetPrompt(
        id="mockup_dashboard_web",
        tipo="mockup",
        version="1.0",
        prompt_template=(
            "MacBook Pro mockup showing a modern business dashboard, dark theme, "
            "charts, KPIs, AI insights panel, customer list, real-time data, "
            "professional design, blue/purple accents, clean layout"
        ),
        provider="figma",
        score=81.0,
        evaluaciones=2,
        casos_uso=["demo", "landing"],
    ),

    # --- AUDIOS ---
    "audio_abordaje_warm": AssetPrompt(
        id="audio_abordaje_warm",
        tipo="audio",
        version="1.0",
        prompt_template=(
            "Voz César Holguín (clonada): tono cercano, profesional, entusiasta. "
            "Mensaje: presentación + beneficio + diagnóstico gratis + call to action. "
            "Duración: 20-30 segundos. Velocidad natural."
        ),
        provider="elevenlabs",
        score=80.0,
        evaluaciones=2,
        casos_uso=["follow_up", "lead_warm"],
    ),
    "audio_abordaje_hot": AssetPrompt(
        id="audio_abordaje_hot",
        tipo="audio",
        version="1.0",
        prompt_template=(
            "Voz César Holguín (clonada): tono urgente, directo, confidente. "
            "Mensaje: confirmación cita + preparar reunión + datos empresa. "
            "Duración: 15-20 segundos. Velocidad ligeramente rápida."
        ),
        provider="elevenlabs",
        score=78.0,
        evaluaciones=1,
        casos_uso=["confirmacion_cita", "lead_hot"],
    ),
}


def get_prompt(asset_type: str, use_case: str = None) -> AssetPrompt | None:
    """Busca prompt por tipo y caso de uso. Retorna el de mayor score."""
    candidates = []
    for p in PROMPTS_EVALUADOS.values():
        if p.tipo == asset_type:
            if use_case is None or use_case in p.casos_uso:
                candidates.append(p)
    if not candidates:
        return None
    return max(candidates, key=lambda x: x.score)


def list_prompts(asset_type: str = None) -> list[AssetPrompt]:
    """Lista prompts disponibles, opcionalmente filtrado por tipo."""
    prompts = list(PROMPTS_EVALUADOS.values())
    if asset_type:
        prompts = [p for p in prompts if p.tipo == asset_type]
    return sorted(prompts, key=lambda x: -x.score)


def evaluate_prompt(prompt_id: str, score: int, feedback: str = "") -> bool:
    """Evalúa un prompt (1-100) y actualiza su score promedio."""
    if prompt_id not in PROMPTS_EVALUADOS:
        return False
    p = PROMPTS_EVALUADOS[prompt_id]
    old_total = p.score * p.evaluaciones
    p.evaluaciones += 1
    p.score = (old_total + score) / p.evaluaciones
    if feedback:
        p.feedback.append(f"[{datetime.utcnow().isoformat()}] {feedback}")
    p.actualizado_en = datetime.utcnow().isoformat()
    return True


def generate_asset_prompt(
    asset_type: str,
    context: dict[str, str],
    use_case: str = None
) -> dict[str, Any]:
    """
    Genera prompt final para un asset específico.
    Combina template evaluado con contexto del usuario.
    Retorna: {prompt_final, provider, parametros, score, version}
    """
    prompt = get_prompt(asset_type, use_case)
    if not prompt:
        return {"error": f"No hay prompts evaluados para tipo={asset_type}, uso={use_case}"}

    # Llenar template con contexto
    final_prompt = prompt.prompt_template
    for key, value in context.items():
        final_prompt = final_prompt.replace(f"{{{key}}}", str(value))

    return {
        "prompt_final": final_prompt,
        "provider": prompt.provider,
        "parametros": prompt.parametros_recomendados,
        "score": prompt.score,
        "version": prompt.version,
        "prompt_id": prompt.id,
        "casos_uso": prompt.casos_uso,
    }


def get_all_prompts_summary() -> str:
    """Resumen legible de todos los prompts para César/Mystic."""
    lines = ["📋 PROMPTS EVALUADOS PARA ASSETS\n"]
    for tipo in ["imagen", "video", "mockup", "audio"]:
        prompts = list_prompts(tipo)
        if prompts:
            lines.append(f"\n🎨 {tipo.upper()}")
            for p in prompts:
                lines.append(f"  [{p.id}] v{p.version} | Score: {p.score:.0f}/100 | {p.provider} | Usos: {', '.join(p.casos_uso)}")

    lines.append(f"\n📊 Total prompts: {len(PROMPTS_EVALUADOS)}")
    lines.append(f"Promedio score: {sum(p.score for p in PROMPTS_EVALUADOS.values()) / len(PROMPTS_EVALUADOS):.1f}/100")
    return "\n".join(lines)


def main():
    """CLI para testing."""
    import argparse
    ap = argparse.ArgumentParser(description="Asset Generation CLI")
    sub = ap.add_subparsers(dest="cmd")

    p_list = sub.add_parser("list", help="Listar prompts")
    p_list.add_argument("--tipo", choices=["imagen", "video", "mockup", "audio"])

    p_get = sub.add_parser("get", help="Obtener prompt")
    p_get.add_argument("--tipo", required=True)
    p_get.add_argument("--uso", help="Caso de uso")

    p_eval = sub.add_parser("evaluate", help="Evaluar prompt")
    p_eval.add_argument("--id", required=True)
    p_eval.add_argument("--score", type=int, required=True)
    p_eval.add_argument("--feedback", default="")

    sub.add_parser("summary", help="Resumen todos los prompts")

    args = ap.parse_args()

    if args.cmd == "list":
        prompts = list_prompts(args.tipo)
        for p in prompts:
            print(f"[{p.id}] v{p.version} | {p.score:.0f}/100 | {p.provider} | {p.casos_uso}")
    elif args.cmd == "get":
        result = generate_asset_prompt(args.tipo, {"servicio": "Aztrotech"}, args.uso)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.cmd == "evaluate":
        ok = evaluate_prompt(args.id, args.score, args.feedback)
        print("OK" if ok else "Prompt no encontrado")
    elif args.cmd == "summary":
        print(get_all_prompts_summary())
    else:
        ap.print_help()


if __name__ == "__main__":
    main()
