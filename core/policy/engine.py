"""
Policy Engine — Orquesta reglas de negocio antes de ejecutar acciones costosas.

Pipeline: Budget → Rate Limit → Approval → Compliance → Execute

Cada acción pasa por este pipeline antes de tocar APIs, GPUs o servicios externos.
"""

import logging
from dataclasses import dataclass
from typing import Callable, Optional

from .inference_budget import BudgetResult, InferenceBudget

logger = logging.getLogger("policy.engine")


@dataclass
class PolicyDecision:
    allowed: bool
    gate: str = ""
    reason: str = ""
    details: Optional[dict] = None

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "gate": self.gate,
            "reason": self.reason,
            "details": self.details or {},
        }


class PolicyEngine:
    """
    Pipeline de gates configurable por tenant.

    Uso:
        engine = PolicyEngine.from_yaml("tenants/aztrotech/policies.yaml")
        decision = await engine.validate("aztrotech", "tts", cost=0.05)
        if decision.allowed:
            # ejecutar acción
            engine.record("aztrotech", "tts", cost=0.05, model="qwen3-tts")
        else:
            # mostrar razón al usuario
            print(decision.reason)
    """

    def __init__(self, budget: Optional[InferenceBudget] = None, rules: Optional[dict] = None):
        self.budget = budget or InferenceBudget()
        self.rules = rules or {}
        self._gates: list[tuple[str, Callable]] = []

    @classmethod
    def from_config(cls, tenant_config: dict, budget: Optional[InferenceBudget] = None):
        """Crea PolicyEngine desde un dict de configuración (ej: policies.yaml)."""
        engine = cls(budget=budget, rules=tenant_config)
        engine._register_gates()
        return engine

    @classmethod
    def from_yaml(cls, yaml_path: str, budget: Optional[InferenceBudget] = None):
        """Crea PolicyEngine desde un archivo YAML."""
        import yaml
        with open(yaml_path) as f:
            config = yaml.safe_load(f) or {}
        tenant_config = config.get("policies", {})
        engine = cls(budget=budget, rules=tenant_config)
        # Configurar límites
        budget_config = tenant_config.get("budget", {})
        for tenant_id, limits in budget_config.items():
            if isinstance(limits, dict):
                engine.budget.set_limits(
                    tenant_id,
                    daily_cap=limits.get("daily_cap", 10.0),
                    max_per_call=limits.get("max_per_call", 2.0),
                )
        engine._register_gates()
        return engine

    def _register_gates(self):
        self._gates = [
            ("budget", self._budget_gate),
            ("rate_limit", self._rate_limit_gate),
            ("approved_models", self._models_gate),
            ("policy", self._business_policy_gate),
        ]

    def _budget_gate(self, tenant: str, action: str, cost: float, context: dict) -> PolicyDecision:
        result = self.budget.can_execute(tenant, cost, action)
        return PolicyDecision(
            allowed=result.allowed,
            gate="budget",
            reason=result.reason,
            details={
                "daily_used": result.daily_used,
                "daily_limit": result.daily_limit,
                "cost": cost,
                "action": action,
            },
        )

    def _rate_limit_gate(self, tenant: str, action: str, cost: float, context: dict) -> PolicyDecision:
        """Rate limit por tenant/acción."""
        rate_limits = self.rules.get("rate_limits", {})
        max_per_min = rate_limits.get(action, rate_limits.get("*", 30))
        # Tracking en memoria simple (se puede mover a Redis)
        now = int(__import__("time").time())
        key = f"rl:{tenant}:{action}"
        bucket = getattr(self, "_rl_buckets", {}).get(key, [])
        bucket = [t for t in bucket if now - t < 60]
        if len(bucket) >= max_per_min:
            return PolicyDecision(
                allowed=False,
                gate="rate_limit",
                reason=f"Demasiadas solicitudes de '{action}' por minuto (máx {max_per_min})",
            )
        bucket.append(now)
        if not hasattr(self, "_rl_buckets"):
            self._rl_buckets = {}
        self._rl_buckets[key] = bucket
        return PolicyDecision(allowed=True, gate="rate_limit")

    def _models_gate(self, tenant: str, action: str, cost: float, context: dict) -> PolicyDecision:
        """Valida que el modelo esté en la lista de permitidos."""
        allowed_models = self.rules.get("allowed_models", {})
        model = context.get("model", "")
        if action in allowed_models and model:
            if model not in allowed_models[action]:
                return PolicyDecision(
                    allowed=False,
                    gate="approved_models",
                    reason=f"Modelo '{model}' no autorizado para '{action}'. Permitidos: {allowed_models[action]}",
                )
        return PolicyDecision(allowed=True, gate="approved_models")

    def _business_policy_gate(self, tenant: str, action: str, cost: float, context: dict) -> PolicyDecision:
        """Reglas de negocio específicas del tenant."""
        business = self.rules.get("business", {})
        rules = business.get(tenant, {}).get("rules", [])

        for rule in rules:
            rule_type = rule.get("type")
            # Ejemplo: bloquear TTS fuera de horario laboral
            if rule_type == "block_hours":
                import datetime
                now = datetime.datetime.now()
                start = rule.get("start", 8)
                end = rule.get("end", 22)
                if now.hour < start or now.hour >= end:
                    return PolicyDecision(
                        allowed=False,
                        gate="policy",
                        reason=rule.get("message", f"Fuera de horario ({start}:00–{end}:00)"),
                    )

            # Ejemplo: requerir confirmación para acciones caras
            if rule_type == "require_confirmation":
                if cost >= rule.get("min_cost", 1.0) and not context.get("confirmed"):
                    return PolicyDecision(
                        allowed=False,
                        gate="policy",
                        reason=rule.get("message", f"Acción de ${cost:.2f} requiere confirmación"),
                        details={"requires_confirmation": True, "estimated_cost": cost},
                    )

        return PolicyDecision(allowed=True, gate="policy")

    async def validate(
        self, tenant: str, action: str, cost: float = 0.0, context: Optional[dict] = None
    ) -> PolicyDecision:
        """Corre todas las gates (async). Si alguna falla, retorna la primera falla."""
        context = context or {}
        for gate_name, gate_fn in self._gates:
            decision = gate_fn(tenant, action, cost, context)
            if not decision.allowed:
                logger.warning(f"[{tenant}] Gate '{gate_name}' bloqueó: {decision.reason}")
                return decision
        return PolicyDecision(allowed=True, gate="all", reason="Todas las gates pasaron")

    def validate_sync(
        self, tenant: str, action: str, cost: float = 0.0, context: Optional[dict] = None
    ) -> PolicyDecision:
        """Corre todas las gates (sync, sin asyncio)."""
        context = context or {}
        for gate_name, gate_fn in self._gates:
            decision = gate_fn(tenant, action, cost, context)
            if not decision.allowed:
                logger.warning(f"[{tenant}] Gate '{gate_name}' bloqueó: {decision.reason}")
                return decision
        return PolicyDecision(allowed=True, gate="all", reason="Todas las gates pasaron")

    def record(self, tenant: str, action: str, cost: float, model: str = ""):
        """Registra uso después de ejecución exitosa."""
        self.budget.record_usage(tenant, action, cost, model)

    def report(self, tenant: str) -> dict:
        return self.budget.daily_report(tenant)
