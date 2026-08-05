"""Base Agent Harness - Marco base para tests de agentes."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional
from uuid import uuid4
import time


@dataclass
class HarnessConfig:
    """Configuración del harness."""
    timeout: float = 30.0
    max_retries: int = 3
    retry_delay: float = 1.0
    mock_responses: dict = field(default_factory=dict)
    pre_hooks: list[Callable] = field(default_factory=list)
    post_hooks: list[Callable] = field(default_factory=list)


@dataclass
class HarnessResult:
    """Resultado de una ejecución del harness."""
    test_id: str
    agent_id: str
    action: str
    input_data: Any
    output_data: Any
    expected: Any
    passed: bool
    duration: float
    error: Optional[str] = None
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow().isoformat()


class AgentHarness:
    """
    Agent Harness - Marco base para tests de agentes.

    Permite:
    - Configurar respuestas mock
    - Ejecutar acciones de forma controlada
    - Verificar resultados
    - Medir rendimiento
    """

    def __init__(self, agent, config: Optional[HarnessConfig] = None):
        self.agent = agent
        self.config = config or HarnessConfig()
        self.results: list[HarnessResult] = []
        self.call_log: list[dict] = []

    def setup(self):
        """Configuración inicial del harness."""
        for hook in self.config.pre_hooks:
            hook(self.agent)

    def teardown(self):
        """Limpieza después del test."""
        for hook in self.config.post_hooks:
            hook(self.agent)

    def mock_response(self, action: str, response: Any):
        """Configura una respuesta mock para una acción."""
        self.config.mock_responses[action] = response

    def execute(
        self,
        action: str,
        inputs: dict,
        expected: Any = None,
        timeout: Optional[float] = None,
    ) -> HarnessResult:
        """
        Ejecuta una acción y verifica el resultado.

        Args:
            action: Acción a ejecutar
            inputs: Datos de entrada
            expected: Resultado esperado (None = no verificar)
            timeout: Timeout personalizado

        Returns:
            HarnessResult con el resultado
        """
        test_id = str(uuid4())
        timeout = timeout or self.config.timeout

        # Registrar llamada
        self.call_log.append({
            "test_id": test_id,
            "action": action,
            "inputs": inputs,
            "timestamp": datetime.utcnow().isoformat(),
        })

        start_time = time.time()

        try:
            # Verificar si hay mock
            if action in self.config.mock_responses:
                output = self.config.mock_responses[action]
            else:
                # Ejecutar acción real
                output = self._execute_action(action, inputs)

            duration = time.time() - start_time

            # Verificar resultado
            passed = True
            if expected is not None:
                passed = self._verify_output(output, expected)

            result = HarnessResult(
                test_id=test_id,
                agent_id=self.agent.agent_id,
                action=action,
                input_data=inputs,
                output_data=output,
                expected=expected,
                passed=passed,
                duration=duration,
            )

        except Exception as e:
            duration = time.time() - start_time
            result = HarnessResult(
                test_id=test_id,
                agent_id=self.agent.agent_id,
                action=action,
                input_data=inputs,
                output_data=None,
                expected=expected,
                passed=False,
                duration=duration,
                error=str(e),
            )

        self.results.append(result)
        return result

    def _execute_action(self, action: str, inputs: dict) -> Any:
        """Ejecuta una acción en el agente."""
        import asyncio
        import concurrent.futures

        from src.agents.base import AgentTask

        task = AgentTask(
            id=str(uuid4()),
            action=action,
            inputs=inputs,
        )

        # Intentar ejecutar de forma asíncrona
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Si ya hay un loop activo, usar ThreadPoolExecutor
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    result = pool.submit(asyncio.run, self.agent.execute(task)).result()
            else:
                result = asyncio.run(self.agent.execute(task))
        except RuntimeError:
            # No hay loop activo, crear uno nuevo
            result = asyncio.run(self.agent.execute(task))

        return result

    def _verify_output(self, output: Any, expected: Any) -> bool:
        """Verifica que el output cumple con lo esperado."""
        if expected is None:
            return True

        # Handle AgentResult objects
        if hasattr(output, 'status') and isinstance(expected, dict):
            for key, value in expected.items():
                if hasattr(output, key):
                    if getattr(output, key) != value:
                        return False
                elif isinstance(output, dict):
                    if key not in output or output[key] != value:
                        return False
            return True

        if isinstance(expected, dict) and isinstance(output, dict):
            for key, value in expected.items():
                if key not in output:
                    return False
                if output[key] != value:
                    return False
            return True

        return output == expected

    def get_stats(self) -> dict:
        """Obtiene estadísticas del harness."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "pass_rate": passed / total if total > 0 else 0,
            "avg_duration": sum(r.duration for r in self.results) / total if total > 0 else 0,
        }

    def assert_all_passed(self):
        """Lanza excepción si algún test falló."""
        failed = [r for r in self.results if not r.passed]
        if failed:
            errors = [f"{r.action}: {r.error or 'Assertion failed'}" for r in failed]
            raise AssertionError(f" {len(failed)} tests failed:\n" + "\n".join(errors))


class MockAgent:
    """
    Mock Agent - Agente mock para tests.

    Permite configurar respuestas personalizadas sin depender de agentes reales.
    """

    def __init__(self, agent_id: str = "mock"):
        self.agent_id = agent_id
        self.name = "Mock Agent"
        self.status = "online"
        self.current_load = 0
        self.max_concurrent = 10
        self.tasks_executed = 0
        self.errors = 0
        self.responses: dict[str, Any] = {}
        self.call_count: dict[str, int] = {}

    def set_response(self, action: str, response: Any):
        """Configura la respuesta para una acción."""
        self.responses[action] = response

    def execute_sync(self, task) -> Any:
        """Ejecuta una tarea mock de forma síncrona."""
        self.call_count[task.action] = self.call_count.get(task.action, 0) + 1
        self.tasks_executed += 1

        if task.action in self.responses:
            return self.responses[task.action]

        return {"status": "success", "action": task.action, "mock": True}

    async def execute(self, task) -> Any:
        """Ejecuta una tarea mock."""
        return self.execute_sync(task)

        return {"status": "success", "action": task.action, "mock": True}

    def get_capabilities(self) -> list[str]:
        """Retorna capacidades mock."""
        return ["mock", "test", "simulation"]

    def get_status(self) -> dict:
        """Retorna estado mock."""
        return {
            "agent_id": self.agent_id,
            "status": self.status,
            "tasks_executed": self.tasks_executed,
            "call_count": self.call_count,
        }
