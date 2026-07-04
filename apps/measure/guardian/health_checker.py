"""Health Checker — verifica salud de todos los servicios vía HTTP/TCP [FR8]"""
import json
import os
import socket
import urllib.request
import urllib.error
from pathlib import Path


REPO = Path(__file__).resolve().parent.parent.parent


def check_http(host, port, path="/", timeout=5):
    """Verifica que un servicio HTTP responda"""
    url = f"http://{host}:{port}{path}"
    try:
        req = urllib.request.Request(url, method="GET")
        resp = urllib.request.urlopen(req, timeout=timeout)
        return {"status": "healthy", "code": resp.status, "url": url}
    except (urllib.error.URLError, socket.timeout, ConnectionRefusedError) as e:
        return {"status": "unhealthy", "error": str(e), "url": url}


def check_tcp(host, port, timeout=3):
    """Verifica que un puerto TCP esté abierto"""
    try:
        s = socket.create_connection((host, port), timeout=timeout)
        s.close()
        return {"status": "healthy", "port": port}
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return {"status": "unhealthy", "error": str(e), "port": port}


def get_targets():
    """Retorna lista de targets desde fleet.yml"""
    fleet = REPO / "fleet.yml"
    if not fleet.exists():
        return []

    import yaml
    with open(fleet) as f:
        data = yaml.safe_load(f)
    return data.get("health", {}).get("blackbox_targets", [])


def check_all():
    """Verifica todos los targets y retorna resultados"""
    targets = get_targets()
    results = []
    for target in targets:
        if target.startswith("http"):
            # http://host:port/path
            parts = target.replace("http://", "").split("/", 1)
            host_port = parts[0]
            path = "/" + parts[1] if len(parts) > 1 else "/"
            if ":" in host_port:
                host, port_str = host_port.rsplit(":", 1)
                port = int(port_str)
            else:
                host = host_port
                port = 80
            result = check_http(host, port, path)
            result["target"] = target
            results.append(result)
        else:
            results.append({"target": target, "status": "unknown", "error": "unsupported protocol"})

    return results


if __name__ == "__main__":
    results = check_all()
    print(json.dumps(results, indent=2))
    healthy = sum(1 for r in results if r["status"] == "healthy")
    total = len(results)
    print(f"\n{healthy}/{total} healthy")
