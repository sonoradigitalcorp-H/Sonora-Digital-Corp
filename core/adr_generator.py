"""ADR Generator — Module 5 of Evolution Engine (HAS-008)
Generates ADR documents from accepted proposals.
"""
from datetime import datetime
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
ADR_DIR = REPO / "evolution" / "adr"


def generate(proposal: dict) -> str | None:
    if proposal.get("status") != "accepted":
        return None

    ADR_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now().strftime("%Y-%m-%d")
    adr_id = f"ADR-evolution-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    content = f"""# {adr_id}

**Date:** {date}
**Status:** Proposed
**Subsystem:** {proposal.get('subsystem', 'unknown')}
**Impact:** {proposal.get('impact', 'medium')}
**Effort:** {proposal.get('effort', 'medium')}

## Context

{proposal.get('description', 'No description provided.')}

## Decision

Implement the proposed change to address the issue.

## Consequences

- Positive: {proposal.get('title', 'Improvement')}
- Negative: Requires verification after implementation
- Risk: Low

## Compliance

HAS-008 § Evolution Engine — Proposer → ADR Generator
"""
    path = ADR_DIR / f"{adr_id}.md"
    path.write_text(content)
    return str(path)
