"""Unit tests for Event Bus."""

import pytest
from src.events.bus import EventBus, Event, EventSubscription


class TestEventBus:
    """Tests del Event Bus."""

    def setup_method(self):
        self.bus = EventBus()

    def test_publish_event(self):
        """Test publicar evento."""
        event = Event(
            id="test-1",
            type="task.created",
            source="dispatcher",
            payload={"task_id": "123"},
        )
        event_id = self.bus.publish(event)
        assert event_id == "test-1"

    def test_publish_invalid_event_type(self):
        """Test publicar evento con tipo inválido."""
        event = Event(
            id="test-1",
            type="invalid.type",
            source="dispatcher",
            payload={},
        )
        with pytest.raises(ValueError):
            self.bus.publish(event)

    def test_subscribe_and_receive(self):
        """Test suscribirse y recibir eventos."""
        received_events = []

        def handler(event):
            received_events.append(event)

        subscription = EventSubscription(
            consumer_id="test-consumer",
            event_types=["task.created"],
            callback=handler,
        )
        self.bus.subscribe(subscription)

        # Publicar evento
        event = Event(
            id="test-1",
            type="task.created",
            source="dispatcher",
            payload={"task_id": "123"},
        )
        self.bus.publish(event)

        assert len(received_events) == 1
        assert received_events[0].type == "task.created"

    def test_list_events(self):
        """Test listar eventos."""
        for i in range(5):
            event = Event(
                id=f"test-{i}",
                type="task.created",
                source="dispatcher",
                payload={"task_id": str(i)},
            )
            self.bus.publish(event)

        events = self.bus.get_events()
        assert len(events) == 5

    def test_list_events_by_type(self):
        """Test listar eventos por tipo."""
        # Publicar eventos de diferentes tipos
        for i in range(3):
            event = Event(
                id=f"test-{i}",
                type="task.created",
                source="dispatcher",
                payload={},
            )
            self.bus.publish(event)

        event = Event(
            id="test-git",
            type="task.completed",
            source="openhands",
            payload={},
        )
        self.bus.publish(event)

        # Filtrar por tipo
        events = self.bus.get_events(event_type="task.created")
        assert len(events) == 3

    def test_get_stats(self):
        """Test obtener estadísticas."""
        event = Event(
            id="test-1",
            type="task.created",
            source="dispatcher",
            payload={},
        )
        self.bus.publish(event)

        stats = self.bus.get_stats()
        assert stats["total_events"] == 1
        assert stats["events_by_type"]["task.created"] == 1

    def test_clear(self):
        """Test limpiar eventos."""
        event = Event(
            id="test-1",
            type="task.created",
            source="dispatcher",
            payload={},
        )
        self.bus.publish(event)

        self.bus.clear()
        assert len(self.bus.events) == 0
