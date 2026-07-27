"""Auto-Provisioning — Despliegue instantáneo de agentes"""

import json
import subprocess
from pathlib import Path
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

REPO = Path(__file__).resolve().parent.parent.parent.parent.parent
PROVISION_SCRIPT = REPO / "products" / "agent-marketplace" / "provisioning" / "provision.sh"

router = APIRouter(prefix="/provision", tags=["provisioning"])


class ProvisionRequest(BaseModel):
    email: str
    phone: str
    package: str
    business_name: str = ""


@router.post("/start")
async def start_provisioning(data: ProvisionRequest):
    """Auto-provision: creates tenant, deploys agents, configures MCPs"""
    # Validate package exists
    pkg_file = REPO / "products" / "agent-marketplace" / "packages" / f"{data.package}.json"
    if not pkg_file.exists():
        raise HTTPException(400, f"Package '{data.package}' not found")

    # Run provisioning script
    cmd = [
        "bash", str(PROVISION_SCRIPT),
        f"--email={data.email}",
        f"--phone={data.phone}",
        f"--package={data.package}",
    ]
    if data.business_name:
        cmd.append(f"--business={data.business_name}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            raise HTTPException(500, f"Provisioning failed: {result.stderr}")

        # Return tenant info
        tenant_id = data.email.split("@")[0][:8]
        return {
            "status": "provisioned",
            "tenant_id": tenant_id,
            "package": data.package,
            "dashboard_url": f"/tenant/{tenant_id}",
            "agents_deployed": json.loads(
                (REPO / "config" / "tenants" / tenant_id / "tenant.json").read_text()
            ).get("agents", []),
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(504, "Provisioning timed out")
    except Exception as e:
        raise HTTPException(500, str(e))


class PackageChangeRequest(BaseModel):
    tenant_id: str
    new_package: str


@router.post("/upgrade")
async def upgrade_package(data: PackageChangeRequest):
    """Upgrade tenant to a higher package"""
    tenant_file = REPO / "config" / "tenants" / data.tenant_id / "tenant.json"
    if not tenant_file.exists():
        raise HTTPException(404, "Tenant not found")

    tenant = json.loads(tenant_file.read_text())
    tenant["package"] = data.new_package
    tenant_file.write_text(json.dumps(tenant, indent=2))

    return {"status": "upgraded", "tenant_id": data.tenant_id, "new_package": data.new_package}
