"""Agent routes."""


from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..registry import AgentRegistry

router = APIRouter()

# Registry instance
registry = AgentRegistry()


class AgentResponse(BaseModel):
    """Agent response model."""
    id: str
    name: str
    description: str
    capabilities: list[str]
    tools_allowed: list[str]
    status: str
    max_concurrent: int
    current_load: int
    available: bool
    last_health_check: str | None = None


@router.get("/agents", response_model=list[AgentResponse])
async def list_agents(
    capability: str | None = None,
    status: str | None = None
):
    """List all agents with optional filters."""
    agents = registry.list_agents(capability=capability, status=status)

    return [
        AgentResponse(
            id=agent.id,
            name=agent.name,
            description=agent.description,
            capabilities=agent.capabilities,
            tools_allowed=agent.tools_allowed,
            status=agent.status,
            max_concurrent=agent.max_concurrent,
            current_load=agent.current_load,
            available=agent.available,
            last_health_check=agent.last_health_check,
        )
        for agent in agents
    ]


@router.get("/agents/stats")
async def agent_stats():
    """Get agent statistics."""
    return registry.get_stats()


@router.get("/agents/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Get agent by ID."""
    agent = registry.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    return AgentResponse(
        id=agent.id,
        name=agent.name,
        description=agent.description,
        capabilities=agent.capabilities,
        tools_allowed=agent.tools_allowed,
        status=agent.status,
        max_concurrent=agent.max_concurrent,
        current_load=agent.current_load,
        available=agent.available,
        last_health_check=agent.last_health_check,
    )


@router.get("/agents/{agent_id}/health")
async def agent_health(agent_id: str):
    """Get agent health status."""
    result = registry.health_check(agent_id)
    if result.get("status") == "error":
        raise HTTPException(status_code=404, detail=result.get("message", "Agent not found"))
    return result

