"""STDIN Listener — Kernel entry point via CLI (HAS-004)
Reads JSON lines from stdin, processes, writes results to stdout.
"""
import json
import logging
import sys

from kernel.main import HermesKernel


logger = logging.getLogger("kernel.stdin")


class StdinListener:
    def __init__(self, kernel: HermesKernel):
        self.kernel = kernel

    async def start(self):
        logger.info("Listening on stdin (JSON lines)...")
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                results = await self.kernel.process(data)
                print(json.dumps(results))
                sys.stdout.flush()
            except json.JSONDecodeError as e:
                print(json.dumps({"error": f"Invalid JSON: {e}"}))
                sys.stdout.flush()
