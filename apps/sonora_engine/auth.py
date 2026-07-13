"""Authorization and permission checks [FR9] — multi-tenant isolation."""

from typing import Any

ALLOWED_ROLES = ("platform_admin", "client_admin", "artist", "fan")

READ_ONLY_ROLES = ("fan",)


def check_permission(
    user_role: str,
    requested_tenant_id: str,
    user_tenant_id: str,
    action: str = "read",
) -> dict[str, Any]:
    """Check if a user has permission to access a tenant's data.

    Rules:
      - platform_admin: access all tenants, all actions
      - client_admin: access own tenant only, read+write
      - artist: access own tenant only, read only
      - fan: access own tenant only, read only
    """
    if user_role not in ALLOWED_ROLES:
        return {"allowed": False, "reason": "Invalid role"}

    # Platform admin bypasses tenant filter
    if user_role == "platform_admin":
        return {"allowed": True, "reason": "Admin access"}

    # Tenant boundary enforcement
    if requested_tenant_id != user_tenant_id:
        return {"allowed": False, "reason": "Tenant access denied"}

    # Read-only roles
    if action == "write" and user_role in READ_ONLY_ROLES:
        return {"allowed": False, "reason": "Read-only role"}

    return {"allowed": True, "reason": "Access granted"}
