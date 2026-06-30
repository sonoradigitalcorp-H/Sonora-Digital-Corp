"""Sales Agent — handles lead capture, qualification, proposals, and deal closure."""

from src.core.agents.agent_base import AgentBase, error_response, success_response
from src.core.sales_pipeline import pipeline


class SalesAgent(AgentBase):
    name = "sales"
    description = "Captura leads, califica, genera propuestas, cierra deals"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> dict:
        ctx = context or {}
        try:
            action = ctx.get("action", "")
            lead_id = ctx.get("lead_id", "")
            if action == "capture":
                lead = pipeline.capture_lead(
                    name=ctx.get("name", ""),
                    email=ctx.get("email", ""),
                    phone=ctx.get("phone", ""),
                    source=ctx.get("source", "manual"),
                    niche=ctx.get("niche", "general"),
                    plan_interest=ctx.get("plan", ""),
                )
                return success_response(f"Lead captured: {lead.id} (score: {lead.score})", lead.__dict__)
            elif action == "qualify":
                lead = pipeline.qualify_lead(lead_id)
                if lead:
                    return success_response(f"Lead qualified: {lead.id} (score: {lead.score})", lead.__dict__)
                return error_response("Lead not found")
            elif action == "proposal":
                proposal = pipeline.generate_proposal(lead_id)
                if proposal:
                    return success_response("Proposal generated", {"proposal": proposal})
                return error_response("Lead not found")
            elif action == "auto_qualify":
                qualified = pipeline.auto_qualify_leads()
                return success_response(f"Auto-qualified {len(qualified)} leads", {"count": len(qualified)})
            elif action == "dashboard":
                return success_response("Pipeline dashboard", pipeline.get_dashboard())
            else:
                return error_response(f"Unknown action: {action}")
        except Exception as e:
            return error_response(str(e))
