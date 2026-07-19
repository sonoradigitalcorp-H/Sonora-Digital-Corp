"""Proposal Generator — Converts patterns into actionable improvement proposals.

Proposal types:
  - CREATE_SKILL: pattern shows missing capability
  - FIX_SKILL: pattern shows skill failing
  - NEW_PRODUCT: pattern shows market opportunity
  - POLICY_CHANGE: pattern shows policy gap
  - INFRA_CHANGE: pattern shows infrastructure issue

Each proposal follows the ADR format (process/templates/ADR.md).
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

REPO = Path(__file__).resolve().parent.parent
PROPOSALS_DIR = REPO / "process" / "active" / "proposals"
TEMPLATE_PATH = REPO / "process" / "templates" / "ADR.md"
PROPOSAL_TYPES = {"CREATE_SKILL", "FIX_SKILL", "NEW_PRODUCT", "POLICY_CHANGE", "INFRA_CHANGE"}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today_str() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _next_id(proposals_dir: Optional[Path] = None) -> str:
    target = proposals_dir or PROPOSALS_DIR
    target.mkdir(parents=True, exist_ok=True)
    existing = list(target.glob("prop-*.json"))
    nums = []
    for p in existing:
        m = re.search(r"prop-(\d+)", p.name)
        if m:
            nums.append(int(m.group(1)))
    next_num = max(nums) + 1 if nums else 1
    return f"prop-{next_num:03d}"


class ProposalGenerator:
    """Converts patterns into actionable proposals following ADR format."""

    def __init__(self, proposals_dir: Optional[Path] = None):
        self.proposals_dir = proposals_dir or PROPOSALS_DIR
        self.proposals_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, patterns: list[dict]) -> list[dict]:
        proposals = []
        for pattern in patterns:
            ptype = pattern.get("type", "")
            proposal = None
            if ptype == "SKILL_GAP":
                proposal = self.generate_from_skill_gap(pattern)
            elif ptype == "FREQUENT_ERROR":
                proposal = self.generate_from_error(pattern)
            elif ptype == "OPPORTUNITY":
                proposal = self.generate_from_opportunity(pattern)
            elif ptype == "REGRESSION":
                proposal = self.generate_from_regression(pattern)
            if proposal:
                proposals.append(proposal)
        return proposals

    def generate_from_skill_gap(self, pattern: dict) -> dict:
        missing = pattern.get("evidence", {}).get("missing_skill", "unknown-skill")
        title = f"Create skill '{missing}' to fill capability gap"
        return self._build_proposal(
            pattern=pattern,
            proposal_type="CREATE_SKILL",
            title=title,
            description=f"Pattern shows that '{missing}' was referenced but no skill exists. "
                        f"Users expect this capability. Creating it would fill a documented gap.",
            action=f"1. Create skills/{missing}/SKILL.md following SKILL-TEMPLATE.md\n"
                   f"2. Register in agents/registry.yaml\n"
                   f"3. Add capability definition\n"
                   f"4. Create tests for the new skill",
            files_to_change=[f"skills/{missing}/SKILL.md", "agents/registry.yaml"],
        )

    def generate_from_error(self, pattern: dict) -> dict:
        evidence = pattern.get("evidence", {})
        err_text = pattern.get("title", "unknown error")
        top_skill = evidence.get("top_skill", "unknown")
        suggestion = pattern.get("suggestion", "Improve error handling")
        return self._build_proposal(
            pattern=pattern,
            proposal_type="FIX_SKILL",
            title=f"Fix frequent error in '{top_skill}': {err_text[:60]}",
            description=f"Error occurred {evidence.get('count', 0)} times across {evidence.get('total', 0)} sessions. "
                        f"Confidence: {pattern.get('confidence', 0):.0%}. "
                        f"Suggestion: {suggestion}",
            action=f"1. Investigate error source in skill '{top_skill}'\n"
                   f"2. Add input validation\n"
                   f"3. Add error handling with retry logic\n"
                   f"4. Test fix with edge cases\n"
                   f"5. Verify error rate drops below threshold",
            files_to_change=[f"skills/{top_skill}/SKILL.md"],
        )

    def generate_from_opportunity(self, pattern: dict) -> dict:
        evidence = pattern.get("evidence", {})
        request = evidence.get("request_excerpt", "unknown feature")
        count = evidence.get("count", 0)
        title = f"Opportunity: implement '{request[:50]}...' ({count} requests)"
        return self._build_proposal(
            pattern=pattern,
            proposal_type="NEW_PRODUCT" if count >= 3 else "CREATE_SKILL",
            title=title,
            description=f"{count} independent users requested the same capability: '{request[:120]}'. "
                        f"This represents unmet demand with pattern confidence of {pattern.get('confidence', 0):.0%}.",
            action=f"1. Define requirements based on user requests\n"
                   f"2. Create SPEC following process\n"
                   f"3. Implement and test\n"
                   f"4. Deploy and monitor adoption",
            files_to_change=["process/active/"],
        )

    def generate_from_regression(self, pattern: dict) -> dict:
        evidence = pattern.get("evidence", {})
        skill = evidence.get("skill", "unknown")
        drop = evidence.get("drop", 0)
        initial = evidence.get("initial_rate", 0)
        latest = evidence.get("latest_rate", 0)
        return self._build_proposal(
            pattern=pattern,
            proposal_type="FIX_SKILL",
            title=f"Investigate regression in '{skill}' (dropped from {initial:.0%} to {latest:.0%})",
            description=f"Skill '{skill}' regressed by {drop:.0%} over {evidence.get('days_analyzed', 0)} days. "
                        f"Was at {initial:.0%} success rate, now at {latest:.0%}. "
                        f"Likely causes: recent deployment, config change, or dependency issue.",
            action=f"1. Review recent changes to skill '{skill}'\n"
                   f"2. Check dependency versions\n"
                   f"3. Roll back if cause is recent deployment\n"
                   f"4. Add regression tests\n"
                   f"5. Monitor for 3 days after fix",
            files_to_change=[f"skills/{skill}/SKILL.md"],
        )

    def evaluate_risk(self, proposal: dict) -> str:
        ptype = proposal.get("type", "")
        if ptype in ("CREATE_SKILL", "NEW_PRODUCT"):
            return "medium"
        if ptype == "FIX_SKILL":
            evidence = proposal.get("evidence", {})
            if isinstance(evidence, dict):
                count = evidence.get("count", 0) if isinstance(evidence, dict) else 0
                if count > 10:
                    return "high"
            return "low"
        if ptype == "POLICY_CHANGE":
            return "medium"
        if ptype == "INFRA_CHANGE":
            return "high"
        return "medium"

    def estimate_impact(self, proposal: dict) -> dict:
        ptype = proposal.get("type", "")
        base = {"score_impact": 1, "time_saved_hours": 0}

        if ptype == "FIX_SKILL":
            evidence = proposal.get("evidence", {})
            count = evidence.get("count", 0) if isinstance(evidence, dict) else 0
            base["score_impact"] = min(5, 1 + count // 3)
            base["time_saved_hours"] = count * 0.5
        elif ptype == "CREATE_SKILL":
            base["score_impact"] = 3
            base["time_saved_hours"] = 2
        elif ptype == "NEW_PRODUCT":
            base["score_impact"] = 5
            base["time_saved_hours"] = 10
        elif ptype == "REGRESSION":
            base["score_impact"] = 4
            base["time_saved_hours"] = 3

        return base

    def save_proposal(self, proposal: dict) -> str:
        proposal_id = proposal.get("proposal_id", _next_id(self.proposals_dir))
        proposal["proposal_id"] = proposal_id
        file_path = self.proposals_dir / f"{proposal_id}.json"
        file_path.write_text(json.dumps(proposal, indent=2, ensure_ascii=False) + "\n")
        self._save_adr(proposal)
        return proposal_id

    def _save_adr(self, proposal: dict) -> None:
        adr_dir = self.proposals_dir / "adr"
        adr_dir.mkdir(parents=True, exist_ok=True)
        today = _today_str().replace("-", "")
        adr_id = f"ADR-{today}-{proposal.get('proposal_id', '000').replace('prop-', '')}"

        template_content = "Architecture Decision Record"
        if TEMPLATE_PATH.exists():
            template_content = TEMPLATE_PATH.read_text()

        adr_content = template_content.replace("{YYYYMMDD}", today).replace("{YYYY-MM-DD}", _today_str())
        adr_content = adr_content.replace("{title}", proposal.get("title", "Untitled"))
        adr_content = adr_content.replace("{NNN}", proposal.get("proposal_id", "000").replace("prop-", ""))

        adr_content = adr_content.replace(
            "{Qué problema resolvíamos, por qué estábamos aquí}",
            f"Pattern detected: {proposal.get('description', 'No description')}"
        )
        adr_content = adr_content.replace(
            "{Qué decidimos hacer}",
            f"Proposal: {proposal.get('action', 'No action defined')}"
        )

        adr_file = adr_dir / f"{adr_id}.md"
        adr_file.write_text(adr_content)

    def list_proposals(self, status: str = "pending") -> list[dict]:
        proposals = []
        for file_path in sorted(self.proposals_dir.glob("prop-*.json")):
            try:
                data = json.loads(file_path.read_text())
                if data.get("status", "pending") == status:
                    proposals.append(data)
            except (json.JSONDecodeError, OSError):
                continue
        return proposals

    def _build_proposal(
        self, pattern: dict, proposal_type: str, title: str,
        description: str, action: str, files_to_change: list[str],
    ) -> dict:
        proposal = {
            "proposal_id": None,
            "pattern_id": pattern.get("pattern_id", "pat-unknown"),
            "type": proposal_type,
            "title": title,
            "status": "pending",
            "risk": "unknown",
            "estimated_score_impact": 1,
            "description": description,
            "action": action,
            "files_to_change": files_to_change,
            "evidence": pattern.get("evidence", {}),
            "tags": pattern.get("tags", []),
            "created_at": _now_iso(),
        }
        proposal["risk"] = self.evaluate_risk(proposal)
        impact = self.estimate_impact(proposal)
        proposal["estimated_score_impact"] = impact["score_impact"]
        proposal["estimated_time_saved_hours"] = impact["time_saved_hours"]
        return proposal
