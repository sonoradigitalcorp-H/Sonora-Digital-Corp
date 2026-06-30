"""
Revenue Pipeline — Sales agent automation for SDC.
Lead → Qualified → Proposal → Negotiation → Won/Lost.
Backed by Neo4j, emits events for score, Engram, gamification.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum

from src.core.domain import Niche
from src.core.gamification import GamificationEngine
from src.core.sdc_business import SDCCustomer, calculate_price, list_plans
from src.core.redis_streams import stream_push

log = logging.getLogger("jarvis.sales_pipeline")

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
EVENTS_FILE = os.path.join(BASE_DIR, "state", "logs", "events.jsonl")
SCORE_LOG = os.path.join(BASE_DIR, "state", "logs", "enterprise-score.log")


class PipelineStage(str, Enum):
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class LeadSource(str, Enum):
    TELEGRAM = "telegram"
    WEB_FORM = "web_form"
    N8N = "n8n"
    WHATSAPP = "whatsapp"
    REFERRAL = "referral"
    MANUAL = "manual"


@dataclass
class Lead:
    id: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    source: str = LeadSource.MANUAL
    niche: str = Niche.GENERAL
    plan_interest: str = ""
    score: int = 0
    stage: str = PipelineStage.LEAD
    notes: str = ""
    created_at: str = ""
    updated_at: str = ""


@dataclass
class Deal:
    id: str = ""
    lead_id: str = ""
    proposal: str = ""
    amount: float = 0.0
    currency: str = "MXN"
    provider: str = ""
    payment_ref: str = ""
    status: str = PipelineStage.LEAD
    lost_reason: str = ""
    created_at: str = ""
    closed_at: str = ""


def _now():
    return datetime.now(timezone.utc).isoformat()


def _emit_event(event: str, payload: dict):
    os.makedirs(os.path.dirname(EVENTS_FILE), exist_ok=True)
    entry = json.dumps({"event": event, "timestamp": _now(), "payload": payload})
    try:
        with open(EVENTS_FILE, "a") as f:
            f.write(entry + "\n")
    except OSError:
        log.warning(f"Could not write event: {event}")
    # Also push to Redis Stream
    try:
        stream_push("events:pipeline", {
            "event": event,
            "timestamp": _now(),
            "payload": json.dumps(payload),
        })
    except Exception:
        pass


def _emit_score_log(stage: str, deal_id: str, amount: float):
    os.makedirs(os.path.dirname(SCORE_LOG), exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    try:
        with open(SCORE_LOG, "a") as f:
            f.write(f"[{ts}] Pipeline: {stage} | deal={deal_id} | amount={amount}\n")
    except OSError:
        pass


class LeadScorer:
    WEIGHTS = {
        "plan_interest": {"imperio": 10, "agente_ia": 7, "conquistador": 5, "explorador": 1},
        "source": {"referral": 8, "telegram": 5, "web_form": 4, "n8n": 3, "whatsapp": 5, "manual": 3},
        "niche": {"empresa": 8, "musica": 6, "ecommerce": 7, "fitness": 5, "educacion": 5, "adulto": 4, "creativo": 4, "general": 2},
    }

    def score(self, lead: Lead) -> int:
        total = 0
        total += self.WEIGHTS["plan_interest"].get(lead.plan_interest, 1)
        total += self.WEIGHTS["source"].get(lead.source, 3)
        total += self.WEIGHTS["niche"].get(lead.niche, 2)
        lead.score = total
        return total

    def is_qualified(self, lead: Lead, threshold: int = 10) -> bool:
        return self.score(lead) >= threshold


class ProposalGenerator:
    def generate(self, lead: Lead) -> str:
        plans = list_plans()
        plan_name = lead.plan_interest or "conquistador"
        plan = next((p for p in plans if p["id"] == plan_name), plans[0])
        price = calculate_price(plan_name, lead.niche)
        features = plan.get("features", [])
        features_list = "\n".join(f"  ✅ {f}" for f in features)

        return f"""📋 **Propuesta para {lead.name}**

**Plan:** {plan['name']}
**Nicho:** {lead.niche}
**Precio:** ${price:,.0f} MXN

**Incluye:**
{features_list}

**¿Cómo pagar?**
• Mercado Pago (tarjeta, OXXO, SPEI) — procesamiento inmediato
• Bitso (USDC, BTC) — 1% fee
• SPEI directo — 0% fee, 24-48 hrs

**Próximo paso:** Confirma tu plan y elige método de pago para empezar hoy.
"""


class SalesPipeline:
    def __init__(self):
        from src.core.neo4j_store import get_driver
        self._driver = get_driver()
        self.scorer = LeadScorer()
        self.proposal_gen = ProposalGenerator()
        self.gamification = GamificationEngine()
        self._init_constraints()

    def _init_constraints(self):
        if not self._driver:
            return
        try:
            with self._driver.session() as session:
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (idx:Lead) REQUIRE idx.id IS UNIQUE")
                session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Deal) REQUIRE d.id IS UNIQUE")
        except Exception as e:
            log.warning(f"Could not create constraints: {e}")

    # ---- Lead Management ----

    def capture_lead(self, name: str = "", email: str = "", phone: str = "",
                     source: str = "manual", niche: str = "general",
                     plan_interest: str = "", notes: str = "") -> Lead:
        lead = Lead(
            id=f"lead_{uuid.uuid4().hex[:12]}",
            name=name,
            email=email,
            phone=phone,
            source=source,
            niche=niche,
            plan_interest=plan_interest,
            stage=PipelineStage.LEAD,
            notes=notes,
            created_at=_now(),
            updated_at=_now(),
        )
        self.scorer.score(lead)
        self._save_neo4j(lead)
        _emit_event("lead_received", {"lead_id": lead.id, "source": source, "niche": niche})
        log.info(f"Lead captured: {lead.id} ({name}) score={lead.score}")
        return lead

    def get_lead(self, lead_id: str) -> Lead | None:
        return self._get_neo4j(lead_id)

    def find_lead_by_email(self, email: str) -> Lead | None:
        if not self._driver or not email:
            return None
        try:
            with self._driver.session() as session:
                result = session.run(
                    "MATCH (idx:Lead) WHERE idx.email = $email RETURN idx",
                    email=email,
                )
                record = result.single()
                if record:
                    return self._node_to_lead(record["idx"])
        except Exception as e:
            log.warning(f"find_lead_by_email error: {e}")
        return None

    def update_lead(self, lead: Lead) -> bool:
        lead.updated_at = _now()
        return self._save_neo4j(lead)

    def qualify_lead(self, lead_id: str, threshold: int = 10) -> Lead | None:
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        if self.scorer.is_qualified(lead, threshold):
            lead.stage = PipelineStage.QUALIFIED
            self.update_lead(lead)
            _emit_event("lead_qualified", {"lead_id": lead.id, "score": lead.score})
            _emit_score_log("lead_qualified", lead.id, 0)
            log.info(f"Lead qualified: {lead.id} score={lead.score}")
        return lead

    def auto_qualify_leads(self, threshold: int = 10) -> list[Lead]:
        leads = self.list_leads(stage=PipelineStage.LEAD)
        qualified = []
        for lead in leads:
            q = self.qualify_lead(lead.id, threshold)
            if q:
                qualified.append(q)
        return qualified

    # ---- Proposal ----

    def generate_proposal(self, lead_id: str) -> str | None:
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        proposal = self.proposal_gen.generate(lead)
        lead.stage = PipelineStage.PROPOSAL
        self.update_lead(lead)
        _emit_event("proposal_generated", {"lead_id": lead.id, "plan": lead.plan_interest})
        return proposal

    # ---- Deal Management ----

    def create_deal(self, lead_id: str, amount: float, currency: str = "MXN",
                    provider: str = "mercadopago") -> Deal | None:
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        deal = Deal(
            id=f"deal_{uuid.uuid4().hex[:12]}",
            lead_id=lead_id,
            amount=amount,
            currency=currency,
            provider=provider,
            status=PipelineStage.NEGOTIATION,
            created_at=_now(),
        )
        self._save_deal_neo4j(deal)
        _emit_event("deal_created", {"deal_id": deal.id, "lead_id": lead_id, "amount": amount})
        return deal

    def accept_proposal(self, lead_id: str) -> bool:
        lead = self.get_lead(lead_id)
        if not lead:
            return False
        lead.stage = PipelineStage.NEGOTIATION
        self.update_lead(lead)
        _emit_event("proposal_accepted", {"lead_id": lead.id})
        return True

    def close_won(self, lead_id: str, payment_ref: str = "", amount: float = 0.0) -> Deal | None:
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        lead.stage = PipelineStage.WON
        self.update_lead(lead)
        deal = Deal(
            id=f"deal_{uuid.uuid4().hex[:12]}",
            lead_id=lead_id,
            amount=amount,
            payment_ref=payment_ref,
            status=PipelineStage.WON,
            created_at=_now(),
            closed_at=_now(),
        )
        self._save_deal_neo4j(deal)
        self._onboard_customer(lead, deal)
        _emit_event("deal_won", {"lead_id": lead.id, "deal_id": deal.id, "amount": amount})
        _emit_score_log("deal_won", deal.id, amount)
        self.gamification.award_xp(lead_id, 100, reason="primera_venta")
        self.gamification.award_badge(lead_id, "primera_venta")
        log.info(f"Deal WON: {deal.id} amount={amount}")
        return deal

    def close_lost(self, lead_id: str, reason: str = "") -> Deal | None:
        lead = self.get_lead(lead_id)
        if not lead:
            return None
        lead.stage = PipelineStage.LOST
        self.update_lead(lead)
        deal = Deal(
            id=f"deal_{uuid.uuid4().hex[:12]}",
            lead_id=lead_id,
            status=PipelineStage.LOST,
            lost_reason=reason,
            created_at=_now(),
            closed_at=_now(),
        )
        self._save_deal_neo4j(deal)
        _emit_event("deal_lost", {"lead_id": lead.id, "deal_id": deal.id, "reason": reason})
        return deal

    # ---- Customer Onboarding ----

    def _onboard_customer(self, lead: Lead, deal: Deal):
        try:
            SDCCustomer(
                id=deal.id,
                nombre=lead.name,
                email=lead.email,
                telefono=lead.phone,
                tipo=lead.niche,
                nicho=lead.niche,
                plan=lead.plan_interest,
                status="active",
            )
            from src.core.neo4j_store import save_memory
            save_memory(f"customer_{deal.id}", json.dumps({
                "name": lead.name,
                "email": lead.email,
                "plan": lead.plan_interest,
                "amount": deal.amount,
                "onboarded_at": _now(),
            }))
            _emit_event("customer_onboarded", {
                "customer_id": deal.id,
                "name": lead.name,
                "plan": lead.plan_interest,
            })
        except Exception as e:
            log.warning(f"Onboarding failed for {lead.id}: {e}")

    # ---- Dashboard ----

    def get_dashboard(self) -> dict:
        stages = {s.value: 0 for s in PipelineStage}
        for lead in self._all_leads_from_neo4j():
            stages[lead.stage] = stages.get(lead.stage, 0) + 1

        total_leads = sum(stages.values())
        won = stages.get(PipelineStage.WON, 0)
        lost = stages.get(PipelineStage.LOST, 0)
        conversion_rate = round(won / max(1, won + lost) * 100, 1)

        deals = self._all_deals_from_neo4j()
        total_revenue = sum(d.amount for d in deals if d.status == PipelineStage.WON)
        pipeline_value = sum(d.amount for d in deals if d.status in (
            PipelineStage.PROPOSAL, PipelineStage.NEGOTIATION))

        return {
            "stages": stages,
            "total_leads": total_leads,
            "won": won,
            "lost": lost,
            "conversion_rate": conversion_rate,
            "total_revenue": total_revenue,
            "pipeline_value": pipeline_value,
            "deals_count": len(deals),
        }

    def list_leads(self, stage: str | None = None) -> list[Lead]:
        leads = self._all_leads_from_neo4j()
        if stage:
            leads = [idx for idx in leads if idx.stage == stage]
        return leads

    # ---- Neo4j Persistence ----

    def _save_neo4j(self, lead: Lead) -> bool:
        if not self._driver:
            return False
        try:
            with self._driver.session() as session:
                session.run(
                    """MERGE (idx:Lead {id: $id})
                       SET idx.name = $name, idx.email = $email, idx.phone = $phone,
                           idx.source = $source, idx.niche = $niche,
                           idx.plan_interest = $plan_interest, idx.score = $score,
                           idx.stage = $stage, idx.notes = $notes,
                           idx.created_at = $created_at, idx.updated_at = $updated_at""",
                    id=lead.id, name=lead.name, email=lead.email, phone=lead.phone,
                    source=lead.source, niche=lead.niche,
                    plan_interest=lead.plan_interest, score=lead.score,
                    stage=lead.stage, notes=lead.notes,
                    created_at=lead.created_at, updated_at=lead.updated_at,
                )
            return True
        except Exception as e:
            log.warning(f"Neo4j save lead error: {e}")
            return False

    def _get_neo4j(self, lead_id: str) -> Lead | None:
        if not self._driver:
            return None
        try:
            with self._driver.session() as session:
                result = session.run("MATCH (idx:Lead {id: $id}) RETURN idx", id=lead_id)
                record = result.single()
                if record:
                    return self._node_to_lead(record["idx"])
        except Exception as e:
            log.warning(f"Neo4j get lead error: {e}")
        return None

    def _all_leads_from_neo4j(self) -> list[Lead]:
        if not self._driver:
            return []
        try:
            with self._driver.session() as session:
                result = session.run("MATCH (idx:Lead) RETURN idx ORDER BY idx.created_at DESC")
                return [self._node_to_lead(record["idx"]) for record in result]
        except Exception as e:
            log.warning(f"Neo4j list leads error: {e}")
            return []

    def _node_to_lead(self, node) -> Lead:
        return Lead(
            id=node.get("id", ""),
            name=node.get("name", ""),
            email=node.get("email", ""),
            phone=node.get("phone", ""),
            source=node.get("source", "manual"),
            niche=node.get("niche", "general"),
            plan_interest=node.get("plan_interest", ""),
            score=node.get("score", 0),
            stage=node.get("stage", PipelineStage.LEAD),
            notes=node.get("notes", ""),
            created_at=node.get("created_at", ""),
            updated_at=node.get("updated_at", ""),
        )

    def _save_deal_neo4j(self, deal: Deal) -> bool:
        if not self._driver:
            return False
        try:
            with self._driver.session() as session:
                session.run(
                    """MERGE (d:Deal {id: $id})
                       SET d.lead_id = $lead_id, d.proposal = $proposal,
                           d.amount = $amount, d.currency = $currency,
                           d.provider = $provider, d.payment_ref = $payment_ref,
                           d.status = $status, d.lost_reason = $lost_reason,
                           d.created_at = $created_at, d.closed_at = $closed_at""",
                    id=deal.id, lead_id=deal.lead_id, proposal=deal.proposal,
                    amount=deal.amount, currency=deal.currency,
                    provider=deal.provider, payment_ref=deal.payment_ref,
                    status=deal.status, lost_reason=deal.lost_reason,
                    created_at=deal.created_at, closed_at=deal.closed_at,
                )
            return True
        except Exception as e:
            log.warning(f"Neo4j save deal error: {e}")
            return False

    def _all_deals_from_neo4j(self) -> list[Deal]:
        if not self._driver:
            return []
        try:
            with self._driver.session() as session:
                result = session.run("MATCH (d:Deal) RETURN d ORDER BY d.created_at DESC")
                return [self._node_to_deal(record["d"]) for record in result]
        except Exception as e:
            log.warning(f"Neo4j list deals error: {e}")
            return []

    def _node_to_deal(self, node) -> Deal:
        return Deal(
            id=node.get("id", ""),
            lead_id=node.get("lead_id", ""),
            proposal=node.get("proposal", ""),
            amount=node.get("amount", 0.0),
            currency=node.get("currency", "MXN"),
            provider=node.get("provider", ""),
            payment_ref=node.get("payment_ref", ""),
            status=node.get("status", PipelineStage.LEAD),
            lost_reason=node.get("lost_reason", ""),
            created_at=node.get("created_at", ""),
            closed_at=node.get("closed_at", ""),
        )


pipeline = SalesPipeline()
