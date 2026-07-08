#!/usr/bin/env python3
"""Hermes Kernel — HAS-004
Central nervous system of the OS.
Processes requests through Context → Planner → Policy → Router → Executor → Reflector.
"""
import argparse
import asyncio
import json
import sys
from pathlib import Path

from kernel.context import ContextEngine
from kernel.planner import Planner
from kernel.policy import PolicyEngine
from kernel.router import AgentRouter
from kernel.executor import Executor
from kernel.reflector import Reflector
from capabilities.bus import CapabilityBus
from agents.runtime import AgentRuntime


ROOT = Path(__file__).resolve().parent.parent


class HermesKernel:
    def __init__(self, config: dict | None = None):
        self.context = ContextEngine()
        self.planner = Planner()
        self.policy = PolicyEngine(config or {})
        self.router = AgentRouter()
        self.executor = Executor()
        self.reflector = Reflector()
        self.config = config or {}
        self.bus = CapabilityBus()
        self.agent_runtime = AgentRuntime()

    async def process(self, raw_input: dict) -> list[dict]:
        ctx = await self.context.build(raw_input)
        tasks = await self.planner.plan(ctx)
        results = []
        for task in tasks:
            gate_results = await self.policy.validate(task)
            if not self.policy.all_passed(gate_results):
                results.append({
                    "task_id": task.id,
                    "status": "rejected",
                    "gates": [g.to_dict() for g in gate_results],
                })
                continue
            agent_id = self.router.route(task)
            result = await self.executor.execute(task, agent_id)
            reflection = await self.reflector.reflect(task, result)
            results.append({
                "task_id": task.id,
                "status": result.status,
                "agent": agent_id,
                "duration_ms": result.duration_ms,
                "output": result.output,
                "reflection": reflection,
            })
        return results

    async def health(self) -> dict:
        return {
            "status": "running",
            "context": self.context.get_stats(),
            "executor": self.executor.get_stats(),
            "agents": len(self.router.list_agents()),
            "agent_runtime": self.agent_runtime.get_stats(),
            "capabilities": len(self.bus.list_status()),
            "capability_list": [c["id"] for c in self.bus.list_status()],
            "config": {"max_cost_per_task": self.config.get("max_cost_per_task", 1.0)},
        }


async def main():
    parser = argparse.ArgumentParser(description="Hermes Kernel (HAS-004)")
    parser.add_argument("--mode", choices=["once", "health"], default="once")
    parser.add_argument("--input", help="JSON input for once mode")
    parser.add_argument("--config", help="Path to kernel config JSON")
    args = parser.parse_args()

    config = {}
    if args.config:
        config_path = Path(args.config)
        if config_path.exists():
            config = json.loads(config_path.read_text())

    kernel = HermesKernel(config)

    if args.mode == "health":
        result = await kernel.health()
        print(json.dumps(result, indent=2))
        return

    if args.mode == "once":
        raw_input = json.loads(args.input or '{"input": "hello"}')
        results = await kernel.process(raw_input)
        print(json.dumps(results, indent=2))
        return


def cli():
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Hermes Kernel (HAS-004)")
    parser.add_argument("--mode", choices=["daemon", "once", "health"], default="once")
    parser.add_argument("--input", help="JSON input for once mode")
    parser.add_argument("--config", help="Path to kernel config JSON")
    parser.add_argument("--host", default="127.0.0.1", help="Bind address (daemon mode)")
    parser.add_argument("--port", type=int, default=8000, help="Bind port (daemon mode)")
    args, _ = parser.parse_known_args()

    if args.mode == "daemon":
        import uvicorn
        print(f"[kernel] Starting daemon on {args.host}:{args.port}")
        uvicorn.run("kernel.app:app", host=args.host, port=args.port, reload=False, log_level="info")
        return

    asyncio.run(main())


if __name__ == "__main__":
    cli()
