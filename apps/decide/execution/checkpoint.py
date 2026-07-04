"""Checkpoint — estado parcial para tareas largas [FR4]"""
import json
from pathlib import Path
from typing import Optional
from .queue import TaskQueue

REPO = Path(__file__).resolve().parent.parent.parent.parent


class CheckpointManager:
    def __init__(self, queue: Optional[TaskQueue] = None):
        self.queue = queue or TaskQueue()
        self.checkpoint_dir = REPO / "state" / "execution" / "checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)

    def save(self, task_id: str, data: dict):
        self.queue.save_checkpoint(task_id, data)
        cpf = self.checkpoint_dir / f"{task_id}.json"
        cpf.write_text(json.dumps(data, indent=2, default=str))

    def load(self, task_id: str) -> Optional[dict]:
        return self.queue.get_checkpoint(task_id)

    def resume(self, task_id: str) -> Optional[dict]:
        cp = self.load(task_id)
        if cp:
            cp["_resumed"] = True
        return cp

    def delete(self, task_id: str):
        cpf = self.checkpoint_dir / f"{task_id}.json"
        if cpf.exists():
            cpf.unlink()
        self.queue.save_checkpoint(task_id, {})
