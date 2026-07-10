import pytest


def test_hermes_client_import():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    assert client is not None


@pytest.mark.asyncio
async def test_hermes_client_call_tool():
    from apps.agents.hermes_client import HermesClient
    client = HermesClient()
    result = await client.call_tool("test", {})
    assert result is not None


def test_monitor_agent_import():
    from apps.agents.monitor_agent import detect_dead_containers
    assert callable(detect_dead_containers)


def test_healer_agent_import():
    from apps.agents.healer_agent import get_dependencies
    assert callable(get_dependencies)


def test_notifier_agent_import():
    from apps.agents.notifier_agent import send_telegram
    assert callable(send_telegram)
