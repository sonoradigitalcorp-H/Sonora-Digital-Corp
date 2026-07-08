"""Policy Engine — Module 3 of Kernel (HAS-004)
Runtime constitution gates: Policy → Security → Cost → Compliance → Quality.
Each task passes through all 5 gates before execution.
"""
from dataclasses import dataclass, field

from kernel.models import KernelTask


@dataclass
class GateResult:
    gate: str
    passed: bool
    rule_id: str = ""
    detail: str = ""
    fix: str = ""

    def to_dict(self) -> dict:
        return {"gate": self.gate, "passed": self.passed, "rule_id": self.rule_id, "detail": self.detail, "fix": self.fix}


class PolicyEngine:
    def __init__(self, config: dict | None = None):
        self.config = config or {}
        self._gates = [
            ("policy", self._policy_gate),
            ("security", self._security_gate),
            ("cost", self._cost_gate),
            ("compliance", self._compliance_gate),
            ("quality", self._quality_gate),
        ]

    async def validate(self, task: KernelTask) -> list[GateResult]:
        results = []
        for name, gate_fn in self._gates:
            result = gate_fn(task)
            results.append(result)
            if not result.passed:
                break
        return results

    def all_passed(self, results: list[GateResult]) -> bool:
        return all(r.passed for r in results)

    def _policy_gate(self, task: KernelTask) -> GateResult:
        if task.priority > 2:
            return GateResult(gate="policy", passed=False, rule_id="POLICY-001",
                              detail=f"Priority {task.priority} exceeds max (2)", fix="Reduce priority to ≤2")
        return GateResult(gate="policy", passed=True)

    def _security_gate(self, task: KernelTask) -> GateResult:
        policies = task.policies or {}
        if policies.get("requires_auth") and not policies.get("auth_token"):
            return GateResult(gate="security", passed=False, rule_id="SEC-001",
                              detail="Task requires authentication but no token provided", fix="Provide auth_token")
        return GateResult(gate="security", passed=True)

    def _cost_gate(self, task: KernelTask) -> GateResult:
        budget = self.config.get("max_cost_per_task", 1.0)
        if task.estimated_cost > budget:
            return GateResult(gate="cost", passed=False, rule_id="COST-001",
                              detail=f"Estimated cost {task.estimated_cost} exceeds budget {budget}",
                              fix=f"Increase budget or reduce complexity")
        return GateResult(gate="cost", passed=True)

    def _compliance_gate(self, task: KernelTask) -> GateResult:
        tenant = task.policies.get("tenant", "default")
        blocked_tenants = self.config.get("blocked_tenants", [])
        if tenant in blocked_tenants:
            return GateResult(gate="compliance", passed=False, rule_id="COMP-001",
                              detail=f"Tenant '{tenant}' is blocked", fix="Use an allowed tenant")
        return GateResult(gate="compliance", passed=True)

    def _quality_gate(self, task: KernelTask) -> GateResult:
        if task.capability and not task.capability.startswith("sync-"):
            pass
        return GateResult(gate="quality", passed=True)
