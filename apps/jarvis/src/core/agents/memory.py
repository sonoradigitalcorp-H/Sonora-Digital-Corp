import time
from typing import Any

from src.core.agents.agent_base import AgentBase, match_keywords, success_response


class MemoryAgent(AgentBase):
    name = "memory"
    description = (
        "Gestión de memoria, contexto y biblioteca de experiencia Agent-Evolver"
    )
    timeout = 10

    def __init__(self):
        super().__init__()
        self._mem_store: dict[str, dict[str, Any]] = {}

    async def run(self, task: str, context: dict = None) -> dict[str, Any]:
        self.log.info(f"Memory task: {task[:100]}...")
        if match_keywords(task, ["guarda", "store", "recuerda esto", "acorda"]):
            return self._store(task)
        elif match_keywords(task, ["busca", "recall", "recuerda", "qué sabes"]):
            return self._recall(task)
        elif match_keywords(task, ["olvida", "forget", "borra"]):
            return self._forget(task)
        else:
            return self._list(task)

    def _get_neo4j(self):
        try:
            from src.core.neo4j_store import get_driver

            return get_driver()
        except Exception:
            return None

    def _store(self, task: str) -> dict[str, Any]:
        import re

        match = re.search(r'(?:como|as|key:?|clave:?)\s*["\']?(\w[\w\s-]+)["\']?', task)
        key = match.group(1).strip().lower() if match else f"mem_{int(time.time())}"
        value = task
        entry = {"key": key, "value": value, "timestamp": time.time()}
        driver = self._get_neo4j()
        if driver:
            try:
                with driver.session() as session:
                    session.run(
                        "MERGE (m:Memory {key: $key}) SET m.value = $value, m.timestamp = $timestamp",
                        key=key,
                        value=value,
                        timestamp=entry["timestamp"],
                    )
                self.log.info(f"Stored memory in Neo4j: {key}")
            except Exception as e:
                self.log.warning(f"Neo4j store failed, using in-memory: {e}")
                self._mem_store[key] = entry
        else:
            self._mem_store[key] = entry
        return success_response(self.name, task, action="stored", key=key)

    def _recall(self, task: str) -> dict[str, Any]:
        memories = []
        driver = self._get_neo4j()
        if driver:
            try:
                with driver.session() as session:
                    for record in session.run(
                        """
                        MATCH (m:Memory)
                        WHERE m.key CONTAINS $query OR m.value CONTAINS $query
                        RETURN m.key, m.value, m.timestamp ORDER BY m.timestamp DESC LIMIT 10
                    """,
                        query=task.lower(),
                    ):
                        memories.append(
                            {
                                "key": record["m.key"],
                                "value": record["m.value"],
                                "timestamp": record.get("m.timestamp", 0),
                            }
                        )
            except Exception as e:
                self.log.warning(f"Neo4j recall failed: {e}")
        if not memories:
            memories = [
                v
                for k, v in self._mem_store.items()
                if task.lower() in k or task.lower() in v.get("value", "").lower()
            ][:10]
        return success_response(
            self.name, task, action="recalled", memories=memories, count=len(memories)
        )

    def _forget(self, task: str) -> dict[str, Any]:
        import re

        match = re.search(r'(?:key:?|clave:?)\s*["\']?(\w[\w\s-]+)["\']?', task)
        key = match.group(1).strip().lower() if match else None
        if not key:
            return success_response(
                self.name,
                task,
                action="forgotten",
                message="No key specified, nothing to forget",
            )
        driver = self._get_neo4j()
        if driver:
            try:
                with driver.session() as session:
                    session.run("MATCH (m:Memory {key: $key}) DELETE m", key=key)
            except Exception:
                pass
        self._mem_store.pop(key, None)
        return success_response(self.name, task, action="forgotten", key=key)

    def _list(self, task: str) -> dict[str, Any]:
        memories = []
        driver = self._get_neo4j()
        if driver:
            try:
                with driver.session() as session:
                    for record in session.run(
                        "MATCH (m:Memory) RETURN m.key, m.value, m.timestamp ORDER BY m.timestamp DESC LIMIT 50"
                    ):
                        memories.append(
                            {
                                "key": record["m.key"],
                                "value": record.get("m.value", "")[:100],
                                "timestamp": record.get("m.timestamp", 0),
                            }
                        )
            except Exception:
                pass
        if not memories:
            memories = list(self._mem_store.values())[:50]
        return success_response(
            self.name, task, action="listed", memories=memories, count=len(memories)
        )
