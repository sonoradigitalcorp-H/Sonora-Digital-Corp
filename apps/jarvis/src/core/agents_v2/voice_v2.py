"""VoiceAgentV2 — Voice processing (STT/TTS)."""
from .agent_base_v2 import AgentBaseV2


class VoiceAgentV2(AgentBaseV2):
    name = "voice"
    description = "Voice processing (STT/TTS)"
    timeout = 30

    async def run(self, task: str, context: dict = None) -> dict:
        self.publish("voice_task", task=task[:100])
        result = self.think(f"Procesa este comando de voz: {task}")
        return self.success(task, result=str(result)[:500])
