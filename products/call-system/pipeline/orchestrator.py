import asyncio
import json
import logging
import time
import os
import sys
import glob

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai.stt import transcribe_bytes
from ai.llm import compose_prompt, generate_response
from pipeline.gate_input import check_input
from pipeline.gate_output import check_response, sanitize as sanitize_text
from pipeline.context import detect_objection, get_niche_for_company
from tenant.service import (
    get_tenant, create_tenant, get_lead_type, get_call_history, save_call, _load_tenants
)
from memory.summarizer import generate_summary
from memory.engram_adapter import save_call_summary, get_context
from analytics.scorer import score_interaction, save_score, get_ab_stats
from analytics.ab_testing import assign_variant, register_result
from analytics.evolution_hook import evaluate_and_apply
import yaml

logger = logging.getLogger(__name__)

OBJECTION_COOLDOWN = 30


class CallSession:
    def __init__(self, client_id, ws):
        self.client_id = client_id
        self.ws = ws
        self.tenant = None
        self.transcript_buffer = []
        self.last_objection_time = 0
        self.start_time = time.time()
        self.detected_objection = None
        self.conversation_history = []
        self.ab_variant = "A"

    async def identify_tenant(self, name=None, phone=None, company=None):
        tenant = None
        if name:
            tenant = get_tenant(name=name)
        if not tenant and name:
            # Fuzzy match: buscar por palabra clave del nombre
            for t in (_load_tenants().get("tenants", [])):
                if name.lower() in t.get("name", "").lower():
                    tenant = t
                    break
        if not tenant and phone:
            tenant = get_tenant(phone=phone)
        if not tenant:
            tenant = create_tenant(
                name=name or "Invitado",
                phone=phone or "",
                company=company or "",
                source="inbound_call",
            )
        self.tenant = tenant
        self.ab_variant = tenant.get("ab_variant", "A")

        await self._send("tenant", {
            "name": tenant.get("name", ""),
            "company": tenant.get("company", ""),
            "plan": tenant.get("plan", "trial"),
            "lead_type": get_lead_type(tenant),
            "total_calls": tenant.get("total_calls", 0),
            "skills": tenant.get("skills", []),
        })

        campaigns_path = os.path.join(os.path.dirname(__file__), "..", "campaigns")
        sys.path.insert(0, campaigns_path)
        try:
            from campaigns.orchestrator import get_campaign_summary
            c = get_campaign_summary()
            ab_stats = get_ab_stats()
            ab_text = " · ".join(f"{k}: {v.get('avg',0)} ({v.get('count',0)})" for k,v in ab_stats.items() if v.get('count',0) > 0)
            await self._send("dashboard", {"campaigns": c, "ab": ab_text or "Sin datos aún"})
        except Exception:
            pass

        return tenant

    async def process_audio(self, audio_bytes, sample_rate=16000):
        text = transcribe_bytes(audio_bytes, sample_rate)
        if not text:
            return None

        await self._send("transcript", {"text": text})
        self.transcript_buffer.append(text)

        gate = check_input(text)
        if not gate["passed"]:
            if gate["action"] == "ignore":
                logger.info(f"Input ignorado: {gate['reason']}")
                return None
            elif gate["action"] == "escalate_to_human":
                await self._send("response", {"text": "Te transfiero con un asesor humano. Un momento por favor."})
                return "escalated"
            elif gate["action"] == "warn_and_continue":
                await self._send("response", {"text": "Entiendo. Sigamos."})

        if not self.tenant:
            self.ab_variant = assign_variant("new", "lead")
            await self._auto_register(text)
            return None

        objection_cat, objection_text = detect_objection(text)
        now = time.time()
        if objection_cat and (now - self.last_objection_time) > OBJECTION_COOLDOWN:
            self.detected_objection = objection_text
            self.last_objection_time = now
            logger.info(f"Objeción detectada: {objection_cat} → {objection_text}")

        lead_type = get_lead_type(self.tenant)

        history = get_call_history(self.tenant["id"])
        memory = await get_context(self.tenant["id"])

        campaign = self.tenant.get("campaign", {})
        messages = compose_prompt(
            self.tenant,
            lead_type,
            text,
            self.detected_objection,
            history,
            variant=self.ab_variant,
            conversation_history=self.conversation_history,
            campaign=campaign,
            turn_number=len(self.conversation_history) + 1,
        )

        temp = {"cold": 0.7, "warm": 0.5, "hot": 0.3}.get(lead_type, 0.5)
        response = await generate_response(messages, temperature=temp)

        output_gate = check_response(response, text)
        if not output_gate["passed"]:
            logger.warning(f"Output gate issues: {output_gate['issues']}")
            response = output_gate["sanitized"]
            if "objecion_no_manejada" in output_gate["issues"] and self.detected_objection:
                messages.append({"role": "user", "content": f"La objeción '{self.detected_objection}' no fue manejada. Respóndela específicamente."})
                response = await generate_response(messages, temperature=temp)
                response = sanitize_text(response)

        self.conversation_history.append({"user": text, "assistant": response})
        await self._send("response", {"text": response})
        return response

    async def _auto_register(self, text):
        name = None
        parts = text.lower().split()
        if "soy" in text.lower():
            idx = text.lower().index("soy")
            name = text[idx + 4:].strip().split(",")[0].split(".")[0].strip()
        elif "me llamo" in text.lower():
            idx = text.lower().index("me llamo")
            name = text[idx + 9:].strip().split(",")[0].split(".")[0].strip()

        if name:
            clean_name = name.split()[0].capitalize() if name.split() else name.capitalize()
            tenant = await self.identify_tenant(name=name)
            if tenant:
                await self._send("response", {"text": f"¡Hola {tenant['name']}! Bienvenido de vuelta a Sonora Digital Corp. ¿Qué puedo hacer por ti hoy?"})
                return "identified"
            else:
                await self._send("response", {"text": f"¡Hola {clean_name}! Bienvenido a Sonora Digital Corp. ¿Me puedes decir tu teléfono y empresa para completar tu registro?"})
                return "identified"

        await self._send("response", {"text": "Hola, soy Mystica de Sonora Digital Corp. ¿Cómo te llamas?"})
        return "asked"

    async def end_call(self):
        duration = int(time.time() - self.start_time)
        transcript = "\n".join(self.transcript_buffer)
        conv_text = "\n".join(f"YO: {c['user']}\nMYSTICA: {c['assistant']}" for c in self.conversation_history)

        summary_data = await generate_summary(conv_text, self.tenant or {}, duration)
        tenant_id = self.tenant["id"] if self.tenant else "unknown"

        call = save_call(
            tenant_id=tenant_id,
            direction="inbound",
            duration_sec=duration,
            transcript=transcript,
            summary=summary_data.get("summary", ""),
            sentiment=summary_data.get("sentiment", "neutral"),
            topics=summary_data.get("topics", []),
        )

        await save_call_summary(tenant_id, {
            "date": call["started_at"],
            "duration_sec": duration,
            "summary": summary_data.get("summary", ""),
            "action_items": summary_data.get("action_items", []),
            "sentiment": summary_data.get("sentiment", "neutral"),
            "resolution": summary_data.get("resolution", "no_resuelto"),
            "objections": summary_data.get("objections_detected", []),
            "lead_score_change": summary_data.get("lead_score_change", 0),
        })

        score = score_interaction(
            transcript,
            conv_text,
            bool(self.detected_objection),
            summary_data.get("resolution") != "no_resuelto",
            duration,
        )
        save_score(tenant_id, call["id"], score, self.ab_variant, get_lead_type(self.tenant or {}))
        ab_result = register_result(self.ab_variant, score)

        ab_stats = get_ab_stats()
        scores_dir = os.path.join(os.path.dirname(__file__), "..", "data", "scores")
        all_scores_data = []
        if os.path.exists(scores_dir):
            for fpath in glob.glob(os.path.join(scores_dir, "*.json")):
                with open(fpath) as _f:
                    all_scores_data.append(json.load(_f))

        evolution_result = evaluate_and_apply(ab_stats, all_scores_data)

        logger.info(
            f"Llamada finalizada: {duration}s, tenant={tenant_id}, "
            f"score={score}, variant={self.ab_variant}, "
            f"evolution_applied={evolution_result['applied']}"
        )

    async def _send(self, msg_type, data):
        try:
            payload = {"type": msg_type, **data}
            await self.ws.send_str(json.dumps(payload))
        except Exception as e:
            logger.error(f"Error sending WS message: {e}")
