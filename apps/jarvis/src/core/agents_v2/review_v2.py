"""ReviewAgentV2 — Code review usando Ollama local + HermesClient."""
from .agent_base_v2 import AgentBaseV2


class ReviewAgentV2(AgentBaseV2):
    name = "review"
    description = "Code review y validacion usando Ollama local"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("review_started", task=task[:100])

        review = self.think(
            f"Eres un code reviewer. Revisa este codigo/tarea:\n\n{task[:1000]}\n\n"
            f"Responde SOLO con:\n"
            f"- Puntaje (1-10)\n"
            f"- Problemas encontrados\n"
            f"- Sugerencias"
        )

        self.publish("review_completed", task=task[:100])
        return self.success(task, review=review)
