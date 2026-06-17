import os
import json

from fastapi import APIRouter

from webui.routes.app_state import get_orchestrator

router = APIRouter()


@router.get("/api/skills")
async def list_all_skills():
    skills = []
    oc_dir = os.path.expanduser("~/.openclaw/workspace/skills")
    if os.path.isdir(oc_dir):
        for d in sorted(os.listdir(oc_dir)):
            skill_path = os.path.join(oc_dir, d, "SKILL.md")
            if os.path.isfile(skill_path):
                with open(skill_path) as f:
                    content = f.read()
                desc = ""
                for line in content.split("\n")[:10]:
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip().strip('"')
                        break
                skills.append({"name": d, "description": desc, "source": "openclaw"})
    orch = get_orchestrator()
    for agent in orch.list_agents():
        skills.append(
            {
                "name": agent["name"],
                "description": agent["description"],
                "source": "jarvis",
            }
        )
    return {"skills": sorted(skills, key=lambda x: x["name"]), "total": len(skills)}
