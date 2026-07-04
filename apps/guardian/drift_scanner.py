"""Drift Scanner — verifica truth/ + fleet.yml vs realidad del VPS [FR7]"""
import json
import re
import subprocess
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent.parent
TRUTH = REPO / "truth"


def get_truth_rules(domain=None):
    """Lee reglas desde truth/ YAML files"""
    rules = []
    for f in sorted(TRUTH.glob("*.yaml")):
        try:
            import yaml
            with open(f) as fh:
                data = yaml.safe_load(fh)
            if domain and data.get("domain") != domain:
                continue
            rules.extend(data.get("rules", []))
        except Exception:
            pass
    return rules


def get_actual_services():
    """Retorna lista de servicios reales desde ss y docker"""
    services = []

    # ss -tlnp para procesos nativos
    try:
        result = subprocess.run(
            ["ss", "-tlnp"], capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            m = re.search(r"LISTEN\s+\S+\s+\S+\s+(\S+):(\d+)", line)
            if m:
                host, port = m.group(1), int(m.group(2))
                if host == "0.0.0.0" or host == "*":
                    services.append({"type": "tcp", "port": port, "bind": "0.0.0.0"})
                elif host == "127.0.0.1":
                    services.append({"type": "tcp", "port": port, "bind": "127.0.0.1"})
    except Exception:
        pass

    # docker ps para contenedores
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2:
                name, status = parts[0], parts[1]
                healthy = "healthy" in status or "Up" in status
                services.append({
                    "type": "docker", "name": name, "status": "healthy" if healthy else "unhealthy"
                })
    except Exception:
        pass

    return services


def get_expected_services():
    """Retorna servicios esperados desde fleet.yml"""
    fleet = REPO / "fleet.yml"
    if not fleet.exists():
        return []

    try:
        import yaml
        with open(fleet) as f:
            data = yaml.safe_load(f)
        return data.get("services", [])
    except Exception:
        return []


def scan():
    """Compara servicios reales vs esperados, retorna lista de drifts"""
    actual = get_actual_services()
    expected = get_expected_services()
    drifts = []

    actual_ports = {s["port"] for s in actual if s["type"] == "tcp"}
    actual_docker = {s["name"] for s in actual if s["type"] == "docker"}
    expected_ports = set()
    for s in expected:
        p = s.get("port")
        if isinstance(p, int):
            expected_ports.add(p)
        elif isinstance(p, dict):
            for v in p.values():
                if isinstance(v, int):
                    expected_ports.add(v)
    expected_docker = {s["name"] for s in expected if s.get("docker")}

    for p in sorted(expected_ports - actual_ports):
        expected_svc = next((s for s in expected if s.get("port") == p), {})
        drifts.append({
            "type": "missing", "detail": f"Expected port {p} ({expected_svc.get('name', 'unknown')}) not listening"
        })

    for p in sorted(actual_ports - expected_ports):
        if p not in (22, 80, 443, 53):
            drifts.append({
                "type": "unexpected", "detail": f"Unexpected port {p} listening"
            })

    for d in sorted(expected_docker - actual_docker):
        drifts.append({
            "type": "missing", "detail": f"Expected docker {d} not running"
        })

    for d in sorted(actual_docker - expected_docker):
        if not d.startswith("sdc-"):
            continue
        drifts.append({
            "type": "unexpected", "detail": f"Unexpected docker {d} running"
        })

    actual_heap = {}
    for s in actual:
        if s["type"] == "docker":
            actual_heap[s["name"]] = s["status"]

    for e in expected:
        if e.get("docker") and e["name"] in actual_heap:
            if actual_heap[e["name"]] == "unhealthy":
                drifts.append({
                    "type": "unhealthy", "detail": f"Docker {e['name']} is unhealthy"
                })

    return drifts


if __name__ == "__main__":
    drifts = scan()
    if drifts:
        print(json.dumps(drifts, indent=2))
    else:
        print("OK — no drifts detected")
