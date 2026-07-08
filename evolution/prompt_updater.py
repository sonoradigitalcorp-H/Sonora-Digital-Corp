"""Prompt Updater — Module 6 of Evolution Engine (HAS-008)
Updates system prompts and templates based on evolution learnings.
"""
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent
PROMPTS_DIR = REPO / "evolution" / "prompts"


def update(proposal: dict) -> list[str]:
    updated = []
    subsystem = proposal.get("subsystem", "general")
    version_dir = PROMPTS_DIR / "versions" / f"v{_next_version()}"
    version_dir.mkdir(parents=True, exist_ok=True)

    changelog = version_dir / "CHANGELOG.md"
    changelog.write_text(f"# Evolution Prompt Update\n\nDate: {proposal.get('created', 'unknown')}\nSubsystem: {subsystem}\nReason: {proposal.get('description', '')}\n")
    updated.append(str(changelog))

    prompt_file = version_dir / f"{subsystem}-prompt.md"
    prompt_file.write_text(f"# {subsystem.capitalize()} Prompt — Auto-generated\n\nBased on evolution proposal: {proposal.get('id', 'unknown')}\n\nGuidelines:\n- Monitor {subsystem} health\n- Report anomalies\n- Follow HAS standards\n")
    updated.append(str(prompt_file))

    return updated


def _next_version() -> str:
    versions_dir = PROMPTS_DIR / "versions"
    if versions_dir.exists():
        existing = [d.name for d in versions_dir.iterdir() if d.is_dir()]
        if existing:
            nums = [int(v[1:]) for v in existing if v.startswith("v") and v[1:].isdigit()]
            if nums:
                return str(max(nums) + 1)
    return "1.0"
