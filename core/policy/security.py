"""Policy Engine — validates every action against tenant policies.

Enforces:
- Tool allow/block lists
- Prompt injection detection (via Mystic Shield)
- Data masking (PII redaction)
- Tool sandboxing (allowed domains, blocked commands)

Usage:
    from core.policy.engine import PolicyEngine
    engine = PolicyEngine()
    
    # Before executing a tool:
    result = engine.check_tool("astrotech", "vps_execute_command", args={"cmd": "rm -rf /"})
    if not result.allowed:
        return result.reason
    
    # Before sending response:
    safe_response = engine.mask_pii("astrotech", response_text)
"""

import re
from typing import Optional

from core.tenants.resolver import TenantResolver, UnknownTenantError


class PolicyResult:
    def __init__(self, allowed: bool, reason: str = ""):
        self.allowed = allowed
        self.reason = reason

    def __bool__(self):
        return self.allowed


class PolicyEngine:
    def __init__(self):
        self._resolver = TenantResolver()

    # ── Tool Access Control ──

    def check_tool(self, tenant_id: str, tool_name: str, args: Optional[dict] = None) -> PolicyResult:
        ctx = self._resolver.load(tenant_id)

        if tool_name in ctx.blocked_tools:
            return PolicyResult(False, f"Tool '{tool_name}' is blocked for tenant '{tenant_id}'")

        if ctx.allowed_tools and tool_name not in ctx.allowed_tools:
            return PolicyResult(False, f"Tool '{tool_name}' is not in allowed_tools for tenant '{tenant_id}'")

        if args:
            result = self._check_sandbox(ctx, tool_name, args)
            if not result.allowed:
                return result

        return PolicyResult(True)

    def _check_sandbox(self, ctx, tool_name: str, args: dict) -> PolicyResult:
        sandbox = ctx.policies.get("tool_sandbox", {})
        if not sandbox.get("enabled"):
            return PolicyResult(True)

        blocked_cmds = sandbox.get("blocked_commands", [])
        allowed_domains = sandbox.get("allowed_domains", [])

        # Command sandboxing
        cmd = args.get("cmd") or args.get("command") or ""
        for blocked in blocked_cmds:
            if blocked in cmd:
                return PolicyResult(False, f"Command contains blocked pattern: {blocked}")

        # URL/Domain sandboxing
        url = args.get("url") or ""
        if url and allowed_domains and "*" not in allowed_domains:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            if not any(domain.endswith(d.lstrip("*.")) for d in allowed_domains):
                return PolicyResult(False, f"Domain '{domain}' not in allowed_domains")

        return PolicyResult(True)

    # ── PII Masking ──

    PII_PATTERNS = {
        "credit_card": re.compile(r"\b(?:\d[ -]*?){13,16}\b"),
        "email": re.compile(r"\b[\w.+-]+@[\w-]+\.[\w.]+\b"),
        "curp": re.compile(r"\b[A-Z]{4}\d{6}[H,M][A-Z]{5}\d{2}\b"),
        "phone_mx": re.compile(r"\b(\+?52)?1?\d{10}\b"),
    }

    def mask_pii(self, tenant_id: str, text: str) -> str:
        ctx = self._resolver.load(tenant_id)
        masking = ctx.policies.get("data_masking", {})
        if not masking.get("pii_detection"):
            return text

        auto_redact = masking.get("auto_redact", [])
        for pattern_name in auto_redact:
            pattern = self.PII_PATTERNS.get(pattern_name)
            if pattern:
                text = pattern.sub(f"[{pattern_name.upper()}_REDACTED]", text)
        return text

    # ── Prompt Injection Detection ──

    INJECTION_PATTERNS = [
        r"(?i)ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
        r"(?i)forget\s+(all\s+)?(previous|above|prior)",
        r"(?i)you\s+are\s+(now|not\s+really)\s+",
        r"(?i)system\s+prompt",
        r"(?i)reveal\s+(your\s+)?(instructions|prompt|system)",
        r"(?i)act\s+as\s+(if\s+you\s+are|though\s+you\s+are)\s+",
        r"(?i)do\s+not\s+follow\s+",
    ]

    def detect_injection(self, text: str) -> bool:
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, text):
                return True
        return False
