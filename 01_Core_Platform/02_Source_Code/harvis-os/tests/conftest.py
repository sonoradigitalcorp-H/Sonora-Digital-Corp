"""Test configuration and fixtures."""

import pytest
from src.dispatcher.dispatcher import Dispatcher
from src.dispatcher.router import AGENT_CONFIG
from src.registry.registry import AgentRegistry, DEFAULT_AGENTS, AgentInfo
from src.events.bus import EventBus
from src.planner.planner import Planner
from src.memory.context import ContextManager
from src.memory.vector_store import VectorStore
from src.memory.graph_store import GraphStore


def _reset_agent_config():
    """Reset all agent loads to 0 and status to online."""
    for agent_id in AGENT_CONFIG:
        AGENT_CONFIG[agent_id]["current_load"] = 0
        AGENT_CONFIG[agent_id]["status"] = "online"


def _reset_default_agents():
    """Reset DEFAULT_AGENTS to original state."""
    import copy
    originals = {
        "openhands": {"current_load": 0, "status": "online"},
        "opencode": {"current_load": 0, "status": "online"},
        "hermes": {"current_load": 0, "status": "online"},
        "aider": {"current_load": 0, "status": "online"},
        "planner": {"current_load": 0, "status": "online"},
        "data_agent": {"current_load": 0, "status": "online"},
    }
    for agent_id, defaults in originals.items():
        if agent_id in DEFAULT_AGENTS:
            DEFAULT_AGENTS[agent_id].current_load = defaults["current_load"]
            DEFAULT_AGENTS[agent_id].status = defaults["status"]


@pytest.fixture(autouse=True)
def reset_state():
    """Reset all shared state between tests."""
    _reset_agent_config()
    _reset_default_agents()

    # Reset singleton dispatcher in routes
    import src.routes.tasks as tasks_module
    tasks_module.dispatcher = Dispatcher()

    # Reset singleton registry in routes
    import src.routes.agents as agents_module
    agents_module.registry = AgentRegistry()

    yield

    _reset_agent_config()
    _reset_default_agents()


@pytest.fixture
def dispatcher():
    """Fresh Dispatcher instance."""
    return Dispatcher()


@pytest.fixture
def registry():
    """Fresh AgentRegistry instance."""
    return AgentRegistry()


@pytest.fixture
def event_bus():
    """Fresh EventBus instance."""
    return EventBus()


@pytest.fixture
def planner():
    """Fresh Planner instance."""
    return Planner()


@pytest.fixture
def context_manager():
    """Fresh ContextManager instance."""
    return ContextManager()


@pytest.fixture
def vector_store():
    """Fresh VectorStore instance."""
    return VectorStore()


@pytest.fixture
def graph_store():
    """Fresh GraphStore instance."""
    return GraphStore()
