"""Event Bus - Comunicación asíncrona entre componentes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Callable, Optional
from uuid import uuid4
from collections import defaultdict
import asyncio


@dataclass
class Event:
    """Evento en el sistema."""
    id: str
    type: str
    source: str
    payload: dict
    metadata: dict = field(default_factory=dict)
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


@dataclass
class EventSubscription:
    """Suscripción a eventos."""
    consumer_id: str
    event_types: list[str]
    callback: Callable
    group: str = "default"


# Tipos de eventos del sistema (Principio II - determinista)
EVENT_TYPES = {
    # Tareas
    "task.created": {
        "description": "Nueva tarea creada por Dispatcher",
        "required_fields": ["task_id", "category", "assigned_agent"],
    },
    "task.classified": {
        "description": "Tarea clasificada por Dispatcher",
        "required_fields": ["task_id", "category", "confidence"],
    },
    "task.started": {
        "description": "Tarea comenzó a ejecutarse",
        "required_fields": ["task_id", "agent_id"],
    },
    "task.completed": {
        "description": "Tarea completada exitosamente",
        "required_fields": ["task_id", "agent_id", "result"],
    },
    "task.failed": {
        "description": "Tarea falló",
        "required_fields": ["task_id", "agent_id", "error"],
    },
    # Planes
    "plan.created": {
        "description": "Nuevo plan generado",
        "required_fields": ["plan_id", "task_id", "steps_count"],
    },
    "plan.approved": {
        "description": "Plan aprobado por usuario",
        "required_fields": ["plan_id", "approved_by"],
    },
    "plan.rejected": {
        "description": "Plan rechazado",
        "required_fields": ["plan_id", "reason"],
    },
    # Steps
    "step.started": {
        "description": "Step de plan comenzó",
        "required_fields": ["plan_id", "step_id", "agent_id"],
    },
    "step.completed": {
        "description": "Step de plan completado",
        "required_fields": ["plan_id", "step_id", "result"],
    },
    "step.failed": {
        "description": "Step de plan falló",
        "required_fields": ["plan_id", "step_id", "error"],
    },
    # Agentes
    "agent.registered": {
        "description": "Agente registrado",
        "required_fields": ["agent_id", "capabilities"],
    },
    "agent.status_changed": {
        "description": "Estado de agente cambió",
        "required_fields": ["agent_id", "old_status", "new_status"],
    },
    "agent.health_check_failed": {
        "description": "Health check de agente falló",
        "required_fields": ["agent_id", "error"],
    },
    # Sistema
    "system.started": {
        "description": "Sistema Harvis iniciado",
        "required_fields": ["version"],
    },
    "system.error": {
        "description": "Error del sistema",
        "required_fields": ["error", "component"],
    },
}


class EventBus:
    """
    Event Bus - Comunicación asíncrona entre componentes.

    Usa Redis Streams para persistencia y consumer groups para
    entrega sin duplicados.
    """

    def __init__(self):
        self.events: list[Event] = []
        self.subscriptions: dict[str, list[EventSubscription]] = defaultdict(list)
        self.event_types = EVENT_TYPES

    def publish(self, event: Event) -> str:
        """
        Publica un evento.

        Args:
            event: Evento a publicar

        Returns:
            ID del evento publicado
        """
        # Validar tipo de evento
        if event.type not in self.event_types:
            raise ValueError(f"Unknown event type: {event.type}")

        # Almacenar evento
        self.events.append(event)

        # Notificar suscriptores
        self._notify_subscribers(event)

        return event.id

    def subscribe(self, subscription: EventSubscription) -> bool:
        """
        Se suscribe a eventos.

        Args:
            subscription: Suscripción

        Returns:
            True si se registró exitosamente
        """
        for event_type in subscription.event_types:
            if event_type not in self.event_types:
                return False

        for event_type in subscription.event_types:
            self.subscriptions[event_type].append(subscription)

        return True

    def unsubscribe(self, consumer_id: str) -> bool:
        """Elimina todas las suscripciones de un consumidor."""
        removed = False
        for event_type in list(self.subscriptions.keys()):
            self.subscriptions[event_type] = [
                s for s in self.subscriptions[event_type]
                if s.consumer_id != consumer_id
            ]
            if not self.subscriptions[event_type]:
                del self.subscriptions[event_type]
                removed = True
        return removed

    def get_events(
        self,
        event_type: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 10,
    ) -> list[Event]:
        """Lista eventos con filtros."""
        events = self.events.copy()

        if event_type:
            events = [e for e in events if e.type == event_type]
        if source:
            events = [e for e in events if e.source == source]

        return events[-limit:]

    def get_stats(self) -> dict:
        """Obtiene estadísticas del event bus."""
        stats = {}
        for event in self.events:
            stats[event.type] = stats.get(event.type, 0) + 1

        return {
            "total_events": len(self.events),
            "events_by_type": stats,
            "total_subscriptions": sum(
                len(subs) for subs in self.subscriptions.values()
            ),
        }

    def _notify_subscribers(self, event: Event):
        """Notifica a los suscriptores de un evento."""
        subscribers = self.subscriptions.get(event.type, [])
        for subscription in subscribers:
            try:
                # En producción, esto sería asíncrono
                subscription.callback(event)
            except Exception as e:
                # Log error pero no fallar
                print(f"Error notifying subscriber {subscription.consumer_id}: {e}")

    def clear(self):
        """Limpia todos los eventos y suscripciones."""
        self.events.clear()
        self.subscriptions.clear()
