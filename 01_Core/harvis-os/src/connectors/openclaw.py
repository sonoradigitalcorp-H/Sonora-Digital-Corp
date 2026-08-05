"""OpenClaw Connector - Integración con OpenClaw Gateway."""

import httpx
from dataclasses import dataclass, field
from typing import Any, Optional
from datetime import datetime


@dataclass
class OpenClawConfig:
    """Configuración de OpenClaw."""
    gateway_url: str = "http://localhost:18789"
    timeout: float = 30.0
    api_key: Optional[str] = None


@dataclass
class OpenClawTask:
    """Tarea de OpenClaw."""
    id: str
    type: str
    payload: dict
    status: str = "pending"
    created_at: str = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()


class OpenClawConnector:
    """
    OpenClaw Connector - Integración con OpenClaw Gateway.

    Permite:
    - Enviar tareas
    - Consultar estado
    - Recibir resultados
    - Health checks
    """

    def __init__(self, config: Optional[OpenClawConfig] = None):
        self.config = config or OpenClawConfig()
        headers = {"Content-Type": "application/json"}
        if self.config.api_key:
            headers["Authorization"] = f"Bearer {self.config.api_key}"

        self.client = httpx.Client(
            base_url=self.config.gateway_url,
            timeout=self.config.timeout,
            headers=headers,
        )
        self._tasks: list[OpenClawTask] = []

    async def send_task(
        self,
        task_type: str,
        payload: dict,
    ) -> dict:
        """
        Envía tarea a OpenClaw.

        Args:
            task_type: Tipo de tarea
            payload: Datos de la tarea

        Returns:
            Respuesta del gateway
        """
        task = OpenClawTask(
            id=f"task-{len(self._tasks)}",
            type=task_type,
            payload=payload,
        )
        self._tasks.append(task)

        try:
            response = self.client.post(
                "/api/tasks",
                json={
                    "type": task_type,
                    "payload": payload,
                },
            )
            response.raise_for_status()

            result = response.json()
            task.status = "sent"

            return {
                "status": "success",
                "task_id": task.id,
                "result": result,
            }

        except httpx.HTTPError as e:
            task.status = "error"
            return {
                "status": "error",
                "task_id": task.id,
                "error": str(e),
            }

    async def get_status(self) -> dict:
        """
        Obtiene estado del gateway.

        Returns:
            Dict con estado del gateway
        """
        try:
            response = self.client.get("/api/status")
            response.raise_for_status()

            return {
                "status": "healthy",
                "url": self.config.gateway_url,
                "data": response.json(),
            }

        except httpx.HTTPError as e:
            return {
                "status": "unhealthy",
                "url": self.config.gateway_url,
                "error": str(e),
            }

    async def get_task(self, task_id: str) -> dict:
        """
        Obtiene estado de una tarea.

        Args:
            task_id: ID de la tarea

        Returns:
            Dict con estado de la tarea
        """
        try:
            response = self.client.get(f"/api/tasks/{task_id}")
            response.raise_for_status()

            return {
                "status": "success",
                "data": response.json(),
            }

        except httpx.HTTPError as e:
            return {
                "status": "error",
                "error": str(e),
            }

    async def health_check(self) -> dict:
        """
        Health check del gateway.

        Returns:
            Dict con estado de salud
        """
        return await self.get_status()

    def get_tasks(self, limit: int = 10) -> list[OpenClawTask]:
        """Obtiene tareas recientes."""
        return self._tasks[-limit:]

    def get_stats(self) -> dict:
        """Obtiene estadísticas."""
        return {
            "total_tasks": len(self._tasks),
            "tasks_by_status": self._count_by_status(),
        }

    def _count_by_status(self) -> dict:
        counts = {}
        for task in self._tasks:
            counts[task.status] = counts.get(task.status, 0) + 1
        return counts

    def close(self):
        """Cierra el cliente HTTP."""
        self.client.close()
