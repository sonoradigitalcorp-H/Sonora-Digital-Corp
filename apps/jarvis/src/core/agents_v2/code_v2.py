"""CodeAgentV2 — code analysis and generation using Ollama local."""
from .agent_base_v2 import AgentBaseV2


class CodeAgentV2(AgentBaseV2):
    name = "code"
    description = "Code analysis and generation using Ollama local"
    timeout = 60

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("code_task", task=task[:100])

        analysis = self.think(
            f"Eres un asistente de codigo. Analiza o genera codigo para:\n\n{task[:1500]}\n\n"
            f"Responde con el codigo o analisis solicitado."
        )

        self.publish("code_completed", task=task[:100])
        return self.success(task, result=analysis)
