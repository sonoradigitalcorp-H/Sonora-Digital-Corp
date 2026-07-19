"""
Client Learner — learns from client interactions to improve the system.

What it detects:
  - Which services each niche uses most → optimize catalog
  - What questions clients ask before buying → improve onboarding
  - Where clients get stuck → add recovery procedures
  - Which prices are acceptable → adjust pricing
  - Common objections → pre-empt in onboarding flow

Cross-client patterns (privacy-safe, aggregated):
  - "70% of musico clients buy clone service first"
  - "Barbero clients ask about pricing before anything else"
  - "Fitness clients return 3x more than other niches"
"""

from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


class ClientLearner:
    def __init__(self, store=None):
        from memory.client_store import ClientStore
        self.store = store or ClientStore()

    def analyze_client(self, client_id: str) -> dict:
        profile = self.store.get_profile(client_id)
        if not profile:
            return {"client_id": client_id, "error": "not found"}

        interactions = self.store.get_interactions(client_id, limit=1000)
        patterns = self.store.get_patterns(client_id)

        service_usage = Counter(i.get("service", "") for i in interactions if i.get("service"))
        total_tokens = sum(i.get("tokens_used", 0) for i in interactions)
        success_count = sum(1 for i in interactions if i.get("success", True))
        total = len(interactions)
        success_rate = round(success_count / total, 3) if total else 0.0

        satisfaction_scores = [
            i["satisfaction_score"] for i in interactions
            if i.get("satisfaction_score") is not None
        ]
        avg_satisfaction = round(sum(satisfaction_scores) / len(satisfaction_scores), 2) if satisfaction_scores else profile.get("satisfaction_score", 5.0)

        top_service = service_usage.most_common(1)[0][0] if service_usage else None

        return {
            "client_id": client_id,
            "niche": profile.get("niche", "unknown"),
            "total_interactions": total,
            "total_tokens": total_tokens,
            "success_rate": success_rate,
            "avg_satisfaction": avg_satisfaction,
            "top_service": top_service,
            "service_breakdown": dict(service_usage.most_common(5)),
            "patterns_detected": len(patterns),
            "active": profile.get("active", True),
            "days_since_first": self._days_since(profile.get("first_interaction")),
            "days_since_last": self._days_since(profile.get("last_interaction")),
        }

    def analyze_niche(self, niche: str) -> dict:
        clients = self._get_clients_by_niche(niche)
        if not clients:
            return {"niche": niche, "client_count": 0, "error": "no clients in this niche"}

        all_interactions = []
        service_usage = Counter()
        total_tokens = 0
        satisfaction_scores = []
        total_interactions = 0

        for cid in clients:
            interactions = self.store.get_interactions(cid, limit=1000)
            all_interactions.extend(interactions)

            for i in interactions:
                if i.get("service"):
                    service_usage[i["service"]] += 1
                total_tokens += i.get("tokens_used", 0)
                if i.get("satisfaction_score") is not None:
                    satisfaction_scores.append(i["satisfaction_score"])
            total_interactions += len(interactions)

        successes = sum(1 for i in all_interactions if i.get("success", True))
        success_rate = round(successes / len(all_interactions), 3) if all_interactions else 0.0
        avg_sat = round(sum(satisfaction_scores) / len(satisfaction_scores), 2) if satisfaction_scores else 0.0

        top_services = service_usage.most_common(5)
        sticky_services = [s for s, c in top_services if c >= len(clients)]
        return_ratio = self._compute_return_ratio(clients)

        return {
            "niche": niche,
            "client_count": len(clients),
            "total_interactions": total_interactions,
            "total_tokens_spent": total_tokens,
            "success_rate": success_rate,
            "avg_satisfaction": avg_sat,
            "top_services": [{"service": s, "count": c} for s, c in top_services],
            "sticky_services": sticky_services,
            "return_ratio": return_ratio,
            "avg_interactions_per_client": round(total_interactions / len(clients), 1) if clients else 0,
        }

    def analyze_all(self) -> dict:
        clients = self.store.all_clients()
        if not clients:
            return {"total_clients": 0, "niches": {}, "cross_client_patterns": []}

        niches = {}
        all_services = Counter()
        total_interactions = 0
        total_tokens = 0
        satisfaction_scores = []

        for cid in clients:
            profile = self.store.get_profile(cid)
            niche = profile.get("niche", "unknown") if profile else "unknown"
            if niche not in niches:
                niches[niche] = {"client_count": 0, "service_usage": Counter(), "interactions": 0, "tokens": 0}
            niches[niche]["client_count"] += 1

            interactions = self.store.get_interactions(cid, limit=1000)
            for i in interactions:
                if i.get("service"):
                    all_services[i["service"]] += 1
                    niches[niche]["service_usage"][i["service"]] += 1
                total_interactions += 1
                total_tokens += i.get("tokens_used", 0)
                if i.get("satisfaction_score") is not None:
                    satisfaction_scores.append(i["satisfaction_score"])

        avg_satisfaction = round(sum(satisfaction_scores) / len(satisfaction_scores), 2) if satisfaction_scores else 0.0

        cross_patterns = self._generate_cross_patterns(niches, clients)

        niche_summaries = {}
        for n, data in niches.items():
            top_services = [{"service": s, "count": c} for s, c in data["service_usage"].most_common(5)]
            niche_summaries[n] = {
                "client_count": data["client_count"],
                "top_services": top_services,
                "total_interactions": data["interactions"],
            }

        return {
            "total_clients": len(clients),
            "total_interactions": total_interactions,
            "total_tokens_spent": total_tokens,
            "avg_satisfaction": avg_satisfaction,
            "niches": niche_summaries,
            "cross_client_patterns": cross_patterns,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_niche_insights(self) -> list:
        clients = self.store.all_clients()
        if not clients:
            return []

        niches = defaultdict(list)
        for cid in clients:
            profile = self.store.get_profile(cid)
            if profile:
                niches[profile.get("niche", "unknown")].append(cid)

        insights = []
        for niche, cids in sorted(niches.items()):
            if len(cids) < 1:
                continue
            analysis = self.analyze_niche(niche)
            if analysis.get("client_count", 0) == 0:
                continue

            top = analysis.get("top_services", [])
            first_service = top[0]["service"] if top else "none"
            insight = (
                f"{analysis['client_count']} client(s) in '{niche}' niche. "
                f"Most used service: '{first_service}' "
                f"({top[0]['count']}x)" if top else f"{analysis['client_count']} client(s) in '{niche}' niche."
            )
            if analysis.get("return_ratio", 0) > 1.5:
                insight += f" High return rate ({analysis['return_ratio']}x)."
            if analysis.get("success_rate", 0) > 0.9:
                insight += " Excellent success rate."
            elif analysis.get("success_rate", 0) < 0.6:
                insight += " Low success rate — may need intervention."

            insights.append({
                "niche": niche,
                "client_count": analysis["client_count"],
                "insight": insight,
                "top_services": analysis.get("top_services", []),
                "success_rate": analysis.get("success_rate", 0),
                "return_ratio": analysis.get("return_ratio", 0),
            })

        return insights

    def get_recommendation(self, client_id: str) -> str:
        profile = self.store.get_profile(client_id)
        if not profile:
            return "Client not found."

        analysis = self.analyze_client(client_id)
        niche = profile.get("niche", "unknown")
        top_service = analysis.get("top_service")

        if not analysis.get("active"):
            return f"Client '{client_id}' is inactive. Consider re-engagement campaign."

        if top_service:
            if analysis.get("success_rate", 1) < 0.7:
                return (
                    f"Client '{profile.get('name', client_id)}' uses '{top_service}' but "
                    f"has a low success rate ({analysis['success_rate']:.0%}). "
                    f"Check for issues with this service for {niche} clients."
                )
            return (
                f"Client '{profile.get('name', client_id)}' ({niche}) responds well to "
                f"'{top_service}'. Consider suggesting '{top_service}' upgrades or bundles."
            )

        return (
            f"Client '{profile.get('name', client_id)}' ({niche}) has no clear service preference yet. "
            f"Guide them through onboarding to discover their needs."
        )

    def generate_insight_report(self) -> str:
        analysis = self.analyze_all()
        niches = analysis.get("niches", {})
        patterns = analysis.get("cross_client_patterns", [])

        lines = [
            "=" * 60,
            "CLIENT LEARNING REPORT",
            "=" * 60,
            f"  Generated: {analysis.get('generated_at', 'N/A')}",
            f"  Total Clients: {analysis.get('total_clients', 0)}",
            f"  Total Interactions: {analysis.get('total_interactions', 0)}",
            f"  Total Tokens Spent: {analysis.get('total_tokens_spent', 0)}",
            f"  Avg Satisfaction: {analysis.get('avg_satisfaction', 0)} / 10",
            "",
            "  Niches:",
        ]

        for niche_name, data in sorted(niches.items()):
            top = data.get("top_services", [])
            top_str = ", ".join(f"{s['service']} ({s['count']}x)" for s in top[:3]) or "none"
            lines.append(f"    {niche_name:20s}  {data['client_count']:3d} clients  top: {top_str}")

        if patterns:
            lines.extend(["", "  Cross-Client Patterns:"])
            for p in patterns:
                lines.append(f"    • {p.get('pattern', '')}")

        total_clients = analysis.get("total_clients", 0)
        if total_clients == 0:
            lines.extend(["", "  No clients yet. Start onboarding to collect data."])

        lines.append("=" * 60)
        return "\n".join(lines)

    def _get_clients_by_niche(self, niche: str) -> list[str]:
        return [
            cid for cid in self.store.all_clients()
            if (self.store.get_profile(cid) or {}).get("niche") == niche
        ]

    def _compute_return_ratio(self, client_ids: list[str]) -> float:
        ratios = []
        for cid in client_ids:
            profile = self.store.get_profile(cid)
            if profile:
                total = profile.get("total_interactions", 0)
                ratios.append(total)
        if not ratios:
            return 0.0
        avg = sum(ratios) / len(ratios)
        return round(avg, 2)

    def _generate_cross_patterns(self, niches: dict, all_client_ids: list[str]) -> list[dict]:
        patterns = []
        for niche, data in niches.items():
            top = data["service_usage"].most_common(1)
            if top:
                service, count = top[0]
                pct = round(count / max(data["client_count"], 1) * 100)
                if pct >= 50:
                    patterns.append({
                        "pattern": f"{pct}% of '{niche}' clients use '{service}' service",
                        "confidence": round(pct / 100, 2),
                        "niche": niche,
                        "service": service,
                    })

        return patterns

    @staticmethod
    def _days_since(iso_str: str | None) -> int:
        if not iso_str:
            return 0
        try:
            dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
            return (datetime.now(timezone.utc) - dt).days
        except (ValueError, TypeError):
            return 0
