"""BDD Step Definitions for Harvis OS."""

import os
import pytest
from pytest_bdd import scenarios, given, when, then, parsers
from src.dispatcher import Dispatcher, IncomingRequest
from src.registry import AgentRegistry
from src.events import EventBus, Event
from src.planner import Planner

# Get the features directory path
FEATURES_DIR = os.path.join(os.path.dirname(__file__), "..", "features")


# ==================== Dispatcher Steps ====================

scenarios(os.path.join(FEATURES_DIR, "dispatcher.feature"))


@pytest.fixture
def dispatcher_instance():
    return Dispatcher()


@given("the Dispatcher is initialized")
def dispatcher_initialized(dispatcher_instance):
    return dispatcher_instance


@when(parsers.parse('I send a task "{task_content}"'))
def send_task(dispatcher_instance, task_content):
    import concurrent.futures
    request = IncomingRequest(
        source="test",
        user_id="test_user",
        content=task_content,
    )
    import asyncio
    with concurrent.futures.ThreadPoolExecutor() as pool:
        dispatcher_instance._current_task = pool.submit(
            asyncio.run, dispatcher_instance.process_request(request)
        ).result()


@then(parsers.parse('the task should be classified as "{category}"'))
def check_category(dispatcher_instance, category):
    task = dispatcher_instance._current_task
    assert task.category == category, f"Expected {category}, got {task.category}"


@then(parsers.parse('the assigned agent should be "{agent}"'))
def check_agent(dispatcher_instance, agent):
    task = dispatcher_instance._current_task
    assert task.assigned_agent == agent, f"Expected {agent}, got {task.assigned_agent}"


@then(parsers.parse("the confidence should be greater than {min_confidence}"))
def check_confidence_min(dispatcher_instance, min_confidence):
    task = dispatcher_instance._current_task
    assert task.confidence > float(min_confidence), f"Confidence {task.confidence} < {min_confidence}"


@then(parsers.parse("the confidence should be exactly {confidence}"))
def check_confidence_exact(dispatcher_instance, confidence):
    task = dispatcher_instance._current_task
    assert task.confidence == float(confidence), f"Expected {confidence}, got {task.confidence}"


# ==================== Planner Steps ====================

scenarios(os.path.join(FEATURES_DIR, "planner.feature"))


@pytest.fixture
def planner_instance():
    return Planner()


@given("the Planner is initialized")
def planner_initialized(planner_instance):
    return planner_instance


@when(parsers.parse('I request a plan for "{task_content}"'))
def request_plan(planner_instance, task_content):
    planner_instance._current_plan = planner_instance.create_plan(
        task_id="test_task",
        content=task_content,
    )


@then(parsers.parse("the plan should have at least {min_steps:d} steps"))
def check_plan_steps(planner_instance, min_steps):
    plan = planner_instance._current_plan
    assert len(plan.steps) >= min_steps, f"Expected >= {min_steps}, got {len(plan.steps)}"


@then(parsers.parse('the plan should require "{agent}" agent'))
def check_plan_agent(planner_instance, agent):
    plan = planner_instance._current_plan
    assert agent in plan.required_agents, f"{agent} not in {plan.required_agents}"


@then(parsers.parse('the plan status should be "{status}"'))
def check_plan_status(planner_instance, status):
    plan = planner_instance._current_plan
    assert plan.status == status, f"Expected {status}, got {plan.status}"


@given("I have a plan")
def have_plan(planner_instance):
    planner_instance._current_plan = planner_instance.create_plan(
        task_id="test_task",
        content="Test task",
    )


@when("I approve the plan")
def approve_plan(planner_instance):
    plan = planner_instance._current_plan
    planner_instance.approve_plan(plan.id)


@when(parsers.parse('I reject the plan with reason "{reason}"'))
def reject_plan(planner_instance, reason):
    plan = planner_instance._current_plan
    planner_instance.reject_plan(plan.id, reason)


# ==================== Registry Steps ====================

scenarios(os.path.join(FEATURES_DIR, "registry.feature"))


@pytest.fixture
def registry_instance():
    return AgentRegistry()


@given("the Agent Registry is initialized")
def registry_initialized(registry_instance):
    return registry_instance


@when("I request the list of agents")
def list_agents(registry_instance):
    registry_instance._current_agents = registry_instance.list_agents()


@then("I should get at least 4 agents")
def check_agent_count(registry_instance):
    agents = registry_instance._current_agents
    assert len(agents) >= 4, f"Expected >= 4, got {len(agents)}"


@then("each agent should have an id, name, and status")
def check_agent_fields(registry_instance):
    agents = registry_instance._current_agents
    for agent in agents:
        assert hasattr(agent, "id"), "Agent missing id"
        assert hasattr(agent, "name"), "Agent missing name"
        assert hasattr(agent, "status"), "Agent missing status"


@when(parsers.parse('I request agent "{agent_id}"'))
def get_agent(registry_instance, agent_id):
    registry_instance._current_agent = registry_instance.get_agent(agent_id)


@then("I should get the agent details")
def check_agent_details(registry_instance):
    agent = registry_instance._current_agent
    assert agent is not None, "Agent not found"


@then(parsers.parse('the agent status should be "{status}"'))
def check_agent_status(registry_instance, status):
    agent = registry_instance._current_agent
    assert agent.status == status, f"Expected {status}, got {agent.status}"


@when(parsers.parse('I check health of agent "{agent_id}"'))
def check_health(registry_instance, agent_id):
    registry_instance._current_health = registry_instance.health_check(agent_id)


@then(parsers.parse('the health status should be "{status}"'))
def check_health_status(registry_instance, status):
    health = registry_instance._current_health
    assert health["status"] == status, f"Expected {status}, got {health['status']}"


@when(parsers.parse('I request agents with capability "{capability}"'))
def list_by_capability(registry_instance, capability):
    registry_instance._current_agents = registry_instance.list_agents(capability=capability)


@then("I should get at least 2 agents")
def check_capability_agents(registry_instance):
    agents = registry_instance._current_agents
    assert len(agents) >= 2, f"Expected >= 2, got {len(agents)}"


@then(parsers.parse('all agents should have "{capability}" capability'))
def check_capability(registry_instance, capability):
    agents = registry_instance._current_agents
    for agent in agents:
        assert capability in agent.capabilities, f"{agent.id} missing {capability}"


# ==================== Event Bus Steps ====================

scenarios(os.path.join(FEATURES_DIR, "events.feature"))


@pytest.fixture
def event_bus_instance():
    return EventBus()


@given("the Event Bus is initialized")
def event_bus_initialized(event_bus_instance):
    return event_bus_instance


@when(parsers.parse('I publish event "{event_type}" from "{source}"'))
def publish_event(event_bus_instance, event_type, source):
    event = Event(
        id="test_event",
        type=event_type,
        source=source,
        payload={"test": True},
    )
    event_bus_instance.publish(event)


@then("the event should be stored")
def check_event_stored(event_bus_instance):
    assert len(event_bus_instance.events) > 0


@then("the event should have a valid id")
def check_event_id(event_bus_instance):
    event = event_bus_instance.events[-1]
    assert event.id is not None


@given("I have published 3 events")
def publish_3_events(event_bus_instance):
    for i in range(3):
        event = Event(
            id=f"event_{i}",
            type="task.created",
            source="dispatcher",
            payload={"index": i},
        )
        event_bus_instance.publish(event)


@when("I request the list of events")
def list_events(event_bus_instance):
    event_bus_instance._current_events = event_bus_instance.get_events()


@then("I should get at least 3 events")
def check_event_count(event_bus_instance):
    events = event_bus_instance._current_events
    assert len(events) >= 3, f"Expected >= 3, got {len(events)}"


@given("I have published events")
def publish_events(event_bus_instance):
    event = Event(
        id="stat_event",
        type="task.created",
        source="dispatcher",
        payload={},
    )
    event_bus_instance.publish(event)


@when("I request event statistics")
def get_stats(event_bus_instance):
    event_bus_instance._current_stats = event_bus_instance.get_stats()


@then("I should get total events count")
def check_total_events(event_bus_instance):
    stats = event_bus_instance._current_stats
    assert "total_events" in stats


@then("I should get events by type breakdown")
def check_events_by_type(event_bus_instance):
    stats = event_bus_instance._current_stats
    assert "events_by_type" in stats
