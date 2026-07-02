"""CLI executor — runs subprocess commands for CLI contract type providers."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

from planner.exceptions import ProviderExecutionError
from planner.models import ProviderRef

log = logging.getLogger("planner.executors.cli")

TIMEOUT = 60


async def execute(provider: ProviderRef, input_data: dict[str, Any]) -> dict[str, Any]:
    """Execute a CLI provider.

    Uses provider.config to determine:
    - binary: executable name/path
    - args: list of arguments (can include {param} placeholders)
    """
    config = provider.config
    binary = config.get("binary", "")
    args = config.get("args", [])
    timeout = config.get("timeout", TIMEOUT)

    if not binary:
        raise ProviderExecutionError(provider.id, provider.id, "No binary configured")

    # Format args with input_data
    formatted_args = []
    for arg in args:
        try:
            formatted_args.append(arg.format(**input_data))
        except KeyError:
            formatted_args.append(arg)

    cmd = [binary] + formatted_args
    log.debug("CLI execute: %s", " ".join(cmd))

    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)

        if proc.returncode != 0:
            raise ProviderExecutionError(
                provider.id, provider.id,
                f"Exit code {proc.returncode}: {stderr.decode()[:200]}"
            )

        return {
            "stdout": stdout.decode(),
            "stderr": stderr.decode(),
            "returncode": proc.returncode,
        }

    except TimeoutError:
        raise ProviderExecutionError(provider.id, provider.id, f"CLI timeout after {timeout}s") from None
    except FileNotFoundError:
        raise ProviderExecutionError(provider.id, provider.id, f"Binary not found: {binary}") from None
    except OSError as e:
        raise ProviderExecutionError(provider.id, provider.id, str(e)) from e
