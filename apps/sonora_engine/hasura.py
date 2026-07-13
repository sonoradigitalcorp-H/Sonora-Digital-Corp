"""Hasura GraphQL client [FR2] — wrapper for queries and mutations."""

import json
import logging
import os
from typing import Any

import httpx

log = logging.getLogger("sonora.engine.hasura")

HASURA_URL = os.getenv("HASURA_URL", "http://localhost:8080/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "")


async def query_async(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute a GraphQL query via Hasura (async)."""
    headers = {"Content-Type": "application/json"}
    if HASURA_ADMIN_SECRET:
        headers["x-hasura-admin-secret"] = HASURA_ADMIN_SECRET

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            HASURA_URL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()


def query(query: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute a GraphQL query via Hasura (sync)."""
    headers = {"Content-Type": "application/json"}
    if HASURA_ADMIN_SECRET:
        headers["x-hasura-admin-secret"] = HASURA_ADMIN_SECRET

    try:
        resp = httpx.post(
            HASURA_URL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        log.error(f"Hasura query failed: {e}")
        return {"data": {}}


def mutate(mutation: str, variables: dict[str, Any] | None = None) -> dict[str, Any]:
    """Execute a GraphQL mutation via Hasura."""
    return query(mutation, variables)
