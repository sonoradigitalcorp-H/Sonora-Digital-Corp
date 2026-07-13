#!/usr/bin/env python3
"""Hasura MCP Server — GraphQL queries and mutations via MCP [FR2].

Exposes Hasura as native MCP tools for agents.
"""

import json
import os

import httpx

HASURA_URL = os.getenv("HASURA_URL", "http://localhost:8080/v1/graphql")
HASURA_ADMIN_SECRET = os.getenv("HASURA_ADMIN_SECRET", "sonora-admin-secret")


async def hasura_query(query: str, variables: dict = None) -> str:
    headers = {"Content-Type": "application/json"}
    if HASURA_ADMIN_SECRET:
        headers["x-hasura-admin-secret"] = HASURA_ADMIN_SECRET
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            HASURA_URL,
            json={"query": query, "variables": variables or {}},
            headers=headers,
            timeout=15,
        )
        return json.dumps(resp.json())


MCP_TOOLS = {
    "hasura_query": {
        "description": "Execute any GraphQL query against Hasura",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "GraphQL query string"},
                "variables": {"type": "object", "description": "Query variables"},
            },
            "required": ["query"],
        },
        "handler": lambda args: hasura_query(args["query"], args.get("variables")),
    },
    "hasura_mutate": {
        "description": "Execute a GraphQL mutation against Hasura",
        "input_schema": {
            "type": "object",
            "properties": {
                "mutation": {"type": "string", "description": "GraphQL mutation string"},
                "variables": {"type": "object", "description": "Mutation variables"},
            },
            "required": ["mutation"],
        },
        "handler": lambda args: hasura_query(args["mutation"], args.get("variables")),
    },
    "hasura_track_table": {
        "description": "Track a PostgreSQL table in Hasura",
        "input_schema": {
            "type": "object",
            "properties": {
                "schema": {"type": "string", "default": "public"},
                "table": {"type": "string", "description": "Table name"},
            },
            "required": ["table"],
        },
        "handler": lambda args: hasura_query(
            "mutation TrackTable($schema: String!, $table: String!) { "
            "track_table(input: {table: {schema: $schema, name: $table}}) "
            "{ table { name } } }",
            {"schema": args.get("schema", "public"), "table": args["table"]},
        ),
    },
}
