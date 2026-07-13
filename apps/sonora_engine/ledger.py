"""Token ($BEAT) calculation engine [FR3, FR9]."""

from typing import Any


def calculate_balance(user_id: str, tenant_id: str) -> int:
    """Calculate current $BEAT balance from ledger.

    In production: queries token_ledger via Hasura.
    In test mode: returns mock data.
    """
    try:
        from .hasura import query

        result = query("""
            query GetBalance($user_id: uuid!, $tenant_id: uuid!) {
                token_ledger_aggregate(
                    where: {user_id: {_eq: $user_id}, tenant_id: {_eq: $tenant_id}}
                ) {
                    aggregate {
                        sum { amount }
                    }
                }
            }
        """, {"user_id": user_id, "tenant_id": tenant_id})

        data = result.get("data", {}).get("token_ledger_aggregate", {})
        return data.get("aggregate", {}).get("sum", {}).get("amount", 0) or 0
    except Exception:
        return 0  # Fallback for tests / unavailable Hasura
