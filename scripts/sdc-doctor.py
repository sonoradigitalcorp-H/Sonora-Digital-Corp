#!/usr/bin/env python3
"""
SDC Doctor — Sonora Digital Corp ecosystem health diagnostic.

A single-file, read-only probe that runs on either the local laptop (user mystic)
or the VPS (user ubuntu / 149.56.46.173) and reports the state of disks, memory,
Docker, systemd services, MCP gateways, WhatsApp wacli, key processes and
listening ports.

Usage:
    python3 scripts/sdc-doctor.py
    python3 scripts/sdc-doctor.py --save /tmp/sdc-doctor-local.json
    python3 scripts/sdc-doctor.py --html
    python3 scripts/sdc-doctor.py --ssh ubuntu@149.56.46.173 --save /tmp/sdc-doctor-full.json

All probes are read-only; this script never modifies system state.
"""

from __future__ import annotations

import argparse
import datetime
import html
import ipaddress
import json
import os
import platform
import re
import shutil
import socket
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# ──────────────────────────────────────────────────────────────────────────────
# Constants and thresholds
# ──────────────────────────────────────────────────────────────────────────────

DISK_WARN_PERCENT = 80.0
MEM_WARN_PERCENT = 90.0
SWAP_WARN_PERCENT = 80.0

SDC_SYSTEMD_PATTERNS = [
    r"^sdc-",
    r"^sonora-",
    r"^openclaw",
    r"^engram",
    r"^omnivoice",
    r"^whatsapp",
    r"^hermes",
    r"^abe",
]

MCP_ENDPOINTS: List[Dict[str, Any]] = [
    {"name": "python-mcp", "url": "http://127.0.0.1:8180/mcp/tools", "type": "tools"},
    {"name": "node-mcp", "url": "http://127.0.0.1:18989", "type": "root"},
    {"name": "adk-runtime", "url": "http://127.0.0.1:6401", "type": "root"},
]

KEY_PROCESSES = [
    "wacli",
    "openclaw",
    "engram",
    "omnivoice-agent",
]

KEY_PORTS = [5432, 6379, 7687, 6333, 5678, 8901, 9090, 18789, 8180, 18989, 6401]

HTML_REPORT_PATH = Path("/tmp/sdc-doctor-report.html")


# ──────────────────────────────────────────────────────────────────────────────
# Helper utilities
# ──────────────────────────────────────────────────────────────────────────────

def _run(
    cmd: List[str],
    *,
    timeout: int = 15,
    shell: bool = False,
    check: bool = False,
) -> Tuple[int, str, str]:
    """Run a command read-only and return (returncode, stdout, stderr)."""
    if not shell:
        executable = shutil.which(cmd[0])
        if executable is None:
            return 127, "", f"{cmd[0]}: command not found"
        cmd[0] = executable
    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=timeout,
            shell=shell,
        )
        return proc.returncode, proc.stdout, proc.stderr
    except subprocess.TimeoutExpired:
        return 124, "", "command timed out"
    except Exception as exc:  # noqa: BLE001
        return 1, "", str(exc)


def _warn(status: str, message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Build a warning/status block."""
    block: Dict[str, Any] = {"status": status, "message": message}
    if details:
        block["details"] = details
    return block


def _now_iso() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def detect_environment() -> Dict[str, Any]:
    """Best-effort auto-detection of the host environment."""
    env = {
        "hostname": platform.node(),
        "platform": platform.platform(),
        "user": os.environ.get("USER") or os.environ.get("USERNAME"),
        "home": os.path.expanduser("~"),
        "cwd": os.getcwd(),
        "python_version": platform.python_version(),
    }

    # Try to infer role from network / user / hostname hints.
    role_guesses = []
    if env["user"] == "ubuntu":
        role_guesses.append("vps")
    if env["user"] == "mystic":
        role_guesses.append("laptop")
    if env["hostname"].startswith("sdc-") or "vps" in env["hostname"].lower():
        role_guesses.append("vps")
    if "149.56.46.173" in _run(["hostname", "-I"])[1]:
        role_guesses.append("vps")

    env["role_guess"] = role_guesses[0] if role_guesses else "unknown"
    return env


# ──────────────────────────────────────────────────────────────────────────────
# Probes
# ──────────────────────────────────────────────────────────────────────────────

def probe_disk() -> Dict[str, Any]:
    """Collect disk usage for all mounted filesystems."""
    result: Dict[str, Any] = {"status": "ok", "filesystems": [], "warnings": []}
    code, out, err = _run(["df", "-h"])
    if code != 0:
        result["status"] = "error"
        result["error"] = err or "df failed"
        return result

    lines = out.strip().splitlines()
    if not lines:
        result["status"] = "error"
        result["error"] = "empty df output"
        return result

    header = lines[0].split()
    for line in lines[1:]:
        parts = line.split()
        # df -h may wrap long filesystem names onto the previous line; skip malformed rows.
        if len(parts) < len(header):
            continue
        try:
            use_percent = float(parts[4].rstrip("%"))
        except (IndexError, ValueError):
            use_percent = None
        fs = {
            "filesystem": parts[0],
            "size": parts[1],
            "used": parts[2],
            "available": parts[3],
            "use_percent": use_percent,
            "mounted_on": parts[5] if len(parts) > 5 else "",
        }
        result["filesystems"].append(fs)
        if use_percent is not None and use_percent > DISK_WARN_PERCENT:
            result["warnings"].append(f"Disk {fs['mounted_on']} is {use_percent}% full")

    if result["warnings"]:
        result["status"] = "warn"
    return result


def probe_memory() -> Dict[str, Any]:
    """Collect memory and swap usage from /proc/meminfo."""
    result: Dict[str, Any] = {"status": "ok", "warnings": []}
    meminfo = Path("/proc/meminfo")
    if not meminfo.exists():
        result["status"] = "error"
        result["error"] = "/proc/meminfo not available"
        return result

    values: Dict[str, int] = {}
    for line in meminfo.read_text().splitlines():
        if ":" in line:
            key, raw = line.split(":", 1)
            try:
                values[key.strip()] = int(raw.strip().split()[0])
            except (IndexError, ValueError):
                continue

    def pct(used: int, total: int) -> Optional[float]:
        if total == 0:
            return None
        return round((used / total) * 100, 2)

    mem_total = values.get("MemTotal", 0)
    mem_available = values.get("MemAvailable")
    mem_free = values.get("MemFree", 0)
    mem_buffers = values.get("Buffers", 0)
    mem_cached = values.get("Cached", 0)

    # Prefer MemAvailable; fall back to Free + Buffers + Cached approximation.
    if mem_available is not None:
        mem_used = mem_total - mem_available
    else:
        mem_used = mem_total - mem_free - mem_buffers - mem_cached

    swap_total = values.get("SwapTotal", 0)
    swap_free = values.get("SwapFree", 0)
    swap_used = swap_total - swap_free

    result["memory"] = {
        "total_kb": mem_total,
        "used_kb": max(0, mem_used),
        "available_kb": mem_available,
        "free_kb": mem_free,
        "use_percent": pct(max(0, mem_used), mem_total),
    }
    result["swap"] = {
        "total_kb": swap_total,
        "used_kb": max(0, swap_used),
        "free_kb": swap_free,
        "use_percent": pct(max(0, swap_used), swap_total),
    }

    if result["memory"]["use_percent"] is not None and result["memory"]["use_percent"] > MEM_WARN_PERCENT:
        result["warnings"].append(
            f"Memory usage is {result['memory']['use_percent']}%"
        )
    if result["swap"]["use_percent"] is not None and result["swap"]["use_percent"] > SWAP_WARN_PERCENT:
        result["warnings"].append(
            f"Swap usage is {result['swap']['use_percent']}%"
        )

    if result["warnings"]:
        result["status"] = "warn"
    return result


def probe_docker() -> Dict[str, Any]:
    """List running Docker containers with name, status, ports and health."""
    result: Dict[str, Any] = {"status": "ok", "available": False, "containers": []}
    if shutil.which("docker") is None:
        result["status"] = "not_available"
        result["message"] = "docker command not found"
        return result

    code, out, err = _run(
        [
            "docker",
            "ps",
            "--format",
            "{{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}\t{{.State}}",
        ]
    )
    if code != 0:
        result["status"] = "error"
        result["error"] = err or "docker ps failed"
        return result

    result["available"] = True
    for line in out.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        name, image, status, ports, state = parts[:5]
        container: Dict[str, Any] = {
            "name": name,
            "image": image,
            "status": status,
            "ports": ports,
            "state": state,
        }
        # Try to get health from docker inspect (best-effort).
        hcode, hout, _ = _run(
            ["docker", "inspect", "--format", "{{.State.Health.Status}}", name]
        )
        if hcode == 0 and hout.strip() and hout.strip() != "<no value>":
            container["health"] = hout.strip()
        result["containers"].append(container)

    return result


def probe_systemd() -> Dict[str, Any]:
    """List SDC-related systemd service units and their states."""
    result: Dict[str, Any] = {"status": "ok", "available": False, "services": []}
    if shutil.which("systemctl") is None:
        result["status"] = "not_available"
        result["message"] = "systemctl not found"
        return result

    # Get all loaded service units (active and inactive).
    code, out, err = _run(
        ["systemctl", "list-units", "--type=service", "--all", "--no-pager", "--no-legend"]
    )
    if code != 0:
        result["status"] = "error"
        result["error"] = err or "systemctl list-units failed"
        return result

    result["available"] = True
    seen: set = set()
    for line in out.strip().splitlines():
        parts = line.split(None, 4)
        if len(parts) < 4:
            continue
        unit = parts[0]
        if not unit.endswith(".service"):
            continue
        if unit in seen:
            continue
        if not any(re.search(pat, unit) for pat in SDC_SYSTEMD_PATTERNS):
            continue
        seen.add(unit)
        load_state = parts[1]
        active_state = parts[2]
        sub_state = parts[3]
        description = parts[4] if len(parts) > 4 else ""
        result["services"].append(
            {
                "unit": unit,
                "load": load_state,
                "active": active_state,
                "sub": sub_state,
                "description": description,
            }
        )

    # Also include unit-files that match but are not currently loaded.
    code2, out2, _ = _run(
        ["systemctl", "list-unit-files", "--type=service", "--no-pager", "--no-legend"]
    )
    if code2 == 0:
        for line in out2.strip().splitlines():
            parts = line.split(None, 1)
            if not parts:
                continue
            unit = parts[0]
            if unit in seen:
                continue
            if not any(re.search(pat, unit) for pat in SDC_SYSTEMD_PATTERNS):
                continue
            seen.add(unit)
            result["services"].append(
                {
                    "unit": unit,
                    "load": "unknown",
                    "active": "inactive",
                    "sub": "unknown",
                    "description": parts[1] if len(parts) > 1 else "",
                }
            )

    failed = [s for s in result["services"] if s["active"] == "failed"]
    if failed:
        result["status"] = "warn"
        result["warnings"] = [f"{s['unit']} is in failed state" for s in failed]
    return result


def _probe_mcp_endpoint(endpoint: Dict[str, Any]) -> Dict[str, Any]:
    """Probe a single MCP/HTTP endpoint."""
    info: Dict[str, Any] = {
        "name": endpoint["name"],
        "url": endpoint["url"],
        "reachable": False,
    }
    try:
        req = urllib.request.Request(
            endpoint["url"],
            headers={"Accept": "application/json"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            info["http_status"] = resp.status
            body = resp.read()
            info["reachable"] = True
            if body:
                try:
                    data = json.loads(body)
                    info["response_json"] = data
                    if endpoint["type"] == "tools" and isinstance(data, dict):
                        # Python MCP usually returns {"tools": [...]}
                        tools = data.get("tools") or data.get("result", {}).get("tools")
                        if isinstance(tools, list):
                            info["tool_count"] = len(tools)
                    elif isinstance(data, dict) and "tools" in data:
                        info["tool_count"] = len(data["tools"])
                except json.JSONDecodeError:
                    info["response_preview"] = body[:256].decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as exc:
        info["http_status"] = exc.code
        info["error"] = f"HTTP {exc.code}"
    except Exception as exc:  # noqa: BLE001
        info["error"] = str(exc)
    return info


def probe_mcp_gateways() -> Dict[str, Any]:
    """Probe known local MCP gateway endpoints."""
    result: Dict[str, Any] = {"status": "ok", "endpoints": []}
    for endpoint in MCP_ENDPOINTS:
        result["endpoints"].append(_probe_mcp_endpoint(endpoint))
    if not any(e.get("reachable") for e in result["endpoints"]):
        result["status"] = "warn"
        result["message"] = "No MCP gateways reachable on localhost"
    return result


def probe_wacli() -> Dict[str, Any]:
    """Check WhatsApp wacli authentication status if available."""
    result: Dict[str, Any] = {"status": "ok", "available": False}
    if shutil.which("wacli") is None:
        result["status"] = "not_available"
        result["message"] = "wacli command not found"
        return result

    code, out, err = _run(["wacli", "auth", "status"])
    result["available"] = True
    result["command_returncode"] = code
    result["output"] = (out + err).strip()

    text = (out + err).lower()
    if "authenticated" in text or "connected" in text:
        result["auth_status"] = "authenticated"
    elif "disconnected" in text or "not authenticated" in text or "unauthorized" in text:
        result["auth_status"] = "disconnected"
        result["status"] = "warn"
    else:
        result["auth_status"] = "unknown"
    return result


def probe_key_processes() -> Dict[str, Any]:
    """Report whether key SDC processes are running."""
    result: Dict[str, Any] = {"status": "ok", "processes": []}
    code, out, err = _run(["ps", "aux"])
    if code != 0:
        result["status"] = "error"
        result["error"] = err or "ps aux failed"
        return result

    ps_lines = out.strip().splitlines()
    for name in KEY_PROCESSES:
        matches = [line for line in ps_lines if name in line and "sdc-doctor" not in line]
        proc: Dict[str, Any] = {"name": name, "running": bool(matches), "instances": []}
        for line in matches:
            parts = line.split(None, 10)
            if len(parts) >= 11:
                proc["instances"].append(
                    {
                        "pid": parts[1],
                        "cpu_percent": parts[2],
                        "mem_percent": parts[3],
                        "command": parts[10],
                    }
                )
        result["processes"].append(proc)
        if not proc["running"]:
            result["status"] = "warn"
    return result


def probe_key_ports() -> Dict[str, Any]:
    """Check whether key SDC ports are listening."""
    result: Dict[str, Any] = {"status": "ok", "ports": []}
    ss_available = shutil.which("ss") is not None
    if not ss_available:
        result["status"] = "not_available"
        result["message"] = "ss command not found"
        return result

    code, out, _ = _run(["ss", "-tlnp"])
    if code != 0:
        result["status"] = "error"
        result["error"] = "ss -tlnp failed"
        return result

    listening = set()
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 4:
            continue
        local = parts[3]
        try:
            # Format is usually [addr]:port or addr:port
            if local.startswith("["):
                port = int(local.rsplit(":", 1)[-1].rstrip("]"))
            else:
                port = int(local.rsplit(":", 1)[-1])
            listening.add(port)
        except (ValueError, IndexError):
            continue

    for port in KEY_PORTS:
        is_listening = port in listening
        result["ports"].append({"port": port, "listening": is_listening})
        if not is_listening:
            result["status"] = "warn"
    return result


# ──────────────────────────────────────────────────────────────────────────────
# Report assembly
# ──────────────────────────────────────────────────────────────────────────────

def build_report(host_label: str = "local") -> Dict[str, Any]:
    """Run all probes and assemble a structured report."""
    report: Dict[str, Any] = {
        "meta": {
            "generated_at": _now_iso(),
            "host_label": host_label,
            "environment": detect_environment(),
        },
        "summary": {"status": "ok", "warnings": []},
    }

    report["disk"] = probe_disk()
    report["memory"] = probe_memory()
    report["docker"] = probe_docker()
    report["systemd"] = probe_systemd()
    report["mcp_gateways"] = probe_mcp_gateways()
    report["wacli"] = probe_wacli()
    report["key_processes"] = probe_key_processes()
    report["key_ports"] = probe_key_ports()

    # Aggregate warnings and overall status.
    statuses = []
    for section in ["disk", "memory", "docker", "systemd", "mcp_gateways", "wacli", "key_processes", "key_ports"]:
        sec = report[section]
        statuses.append(sec.get("status", "unknown"))
        for w in sec.get("warnings", []):
            report["summary"]["warnings"].append(f"[{section}] {w}")

    if "error" in statuses:
        report["summary"]["status"] = "error"
    elif "warn" in statuses:
        report["summary"]["status"] = "warn"
    elif all(s in ("ok", "not_available") for s in statuses):
        report["summary"]["status"] = "ok"
    else:
        report["summary"]["status"] = "unknown"

    return report


# ──────────────────────────────────────────────────────────────────────────────
# HTML report generation
# ──────────────────────────────────────────────────────────────────────────────

def _html_section(title: str, data: Dict[str, Any]) -> str:
    """Render one report section as HTML."""
    status = html.escape(str(data.get("status", "unknown")))
    status_class = f"status-{status.replace('_', '-')}" if status else "status-unknown"
    body = [f'<section><h2>{html.escape(title)} <span class="badge {status_class}">{status}</span></h2>']
    body.append(f"<pre>{html.escape(json.dumps(data, indent=2))}</pre>")
    body.append("</section>")
    return "\n".join(body)


def generate_html(report: Dict[str, Any]) -> str:
    """Generate a pretty HTML report from the JSON report."""
    title = f"SDC Doctor — {report['meta']['host_label']}"
    sections = []
    order = [
        "summary",
        "disk",
        "memory",
        "docker",
        "systemd",
        "mcp_gateways",
        "wacli",
        "key_processes",
        "key_ports",
    ]
    for key in order:
        if key in report:
            sections.append(_html_section(key.replace("_", " ").title(), report[key]))
    for key, value in report.items():
        if key not in order + ["meta"]:
            sections.append(_html_section(key.replace("_", " ").title(), value))

    meta_html = f"""
    <section>
      <h2>Meta</h2>
      <pre>{html.escape(json.dumps(report.get('meta', {}), indent=2))}</pre>
    </section>
    """
    sections_html = "\n".join(sections)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <style>
    :root {{ color-scheme: light dark; }}
    body {{ font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 2rem auto; max-width: 960px; line-height: 1.5; padding: 0 1rem; }}
    h1 {{ font-size: 1.6rem; margin-bottom: 0.25rem; }}
    h2 {{ font-size: 1.15rem; margin-top: 1.75rem; border-bottom: 1px solid #ccc; padding-bottom: 0.25rem; }}
    .timestamp {{ color: #666; font-size: 0.9rem; margin-bottom: 1.5rem; }}
    section {{ margin-bottom: 1.5rem; }}
    pre {{ background: #f4f4f4; padding: 1rem; border-radius: 6px; overflow-x: auto; font-size: 0.85rem; }}
    .badge {{ font-size: 0.75rem; padding: 0.15rem 0.5rem; border-radius: 999px; color: #fff; margin-left: 0.5rem; vertical-align: middle; }}
    .status-ok {{ background: #2e7d32; }}
    .status-warn {{ background: #f9a825; color: #000; }}
    .status-error {{ background: #c62828; }}
    .status-not-available {{ background: #757575; }}
    .status-unknown {{ background: #9e9e9e; }}
    @media (prefers-color-scheme: dark) {{
      body {{ background: #121212; color: #e0e0e0; }}
      pre {{ background: #1e1e1e; }}
      h2 {{ border-color: #444; }}
    }}
  </style>
</head>
<body>
  <h1>{html.escape(title)}</h1>
  <div class="timestamp">Generated: {html.escape(report['meta']['generated_at'])}</div>
  {meta_html}
  {sections_html}
</body>
</html>
"""


# ──────────────────────────────────────────────────────────────────────────────
# SSH remote execution
# ──────────────────────────────────────────────────────────────────────────────

def run_remote(ssh_target: str, local_script_path: Path) -> Dict[str, Any]:
    """Run this script on a remote host over SSH and merge the JSON report."""
    result: Dict[str, Any] = {
        "status": "ok",
        "ssh_target": ssh_target,
        "message": "",
        "remote_report": None,
    }
    if shutil.which("ssh") is None:
        result["status"] = "error"
        result["message"] = "ssh command not found locally"
        return result

    script_bytes = local_script_path.read_bytes()
    # Push the script to the remote /tmp and run it there. Avoids depending on the
    # script already existing on the remote host.
    remote_path = "/tmp/sdc-doctor.py"
    scp = shutil.which("scp") or "scp"
    copy_code, _, copy_err = _run([scp, str(local_script_path), f"{ssh_target}:{remote_path}"])
    if copy_code != 0:
        result["status"] = "error"
        result["message"] = f"failed to copy script to remote: {copy_err}"
        return result

    run_code, run_out, run_err = _run(
        ["ssh", ssh_target, f"python3 {remote_path} --save /tmp/sdc-doctor-remote.json"]
    )
    if run_code != 0:
        result["status"] = "error"
        result["message"] = f"remote execution failed: {run_err or run_out}"
        return result

    fetch_code, fetch_out, fetch_err = _run(
        ["ssh", ssh_target, "cat /tmp/sdc-doctor-remote.json"]
    )
    if fetch_code != 0:
        result["status"] = "error"
        result["message"] = f"failed to fetch remote report: {fetch_err}"
        return result

    try:
        remote_report = json.loads(fetch_out)
        result["remote_report"] = remote_report
    except json.JSONDecodeError as exc:
        result["status"] = "error"
        result["message"] = f"remote report is not valid JSON: {exc}"
    return result


# ──────────────────────────────────────────────────────────────────────────────
# CLI entrypoint
# ──────────────────────────────────────────────────────────────────────────────

def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sonora Digital Corp — read-only ecosystem health diagnostic.",
    )
    parser.add_argument(
        "--save",
        metavar="PATH",
        help="Write the JSON report to PATH.",
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help=f"Generate a pretty HTML report at {HTML_REPORT_PATH}.",
    )
    parser.add_argument(
        "--ssh",
        metavar="USER@HOST",
        help="Run the same probes on a remote host via SSH and merge results.",
    )
    parser.add_argument(
        "--host-label",
        default="local",
        help="Label for this host in the report (default: local).",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    local_report = build_report(host_label=args.host_label)

    if args.ssh:
        script_path = Path(__file__).resolve()
        remote_wrapper = run_remote(args.ssh, script_path)
        local_report["remote"] = remote_wrapper
        if remote_wrapper.get("remote_report"):
            local_report["remote_report"] = remote_wrapper["remote_report"]
            # If either side is unhealthy, bubble it up.
            remote_status = remote_wrapper["remote_report"].get("summary", {}).get("status", "unknown")
            local_status = local_report["summary"]["status"]
            if "error" in (local_status, remote_status):
                local_report["summary"]["status"] = "error"
            elif "warn" in (local_status, remote_status):
                local_report["summary"]["status"] = "warn"

    json_text = json.dumps(local_report, indent=2)

    if args.save:
        save_path = Path(args.save)
        save_path.write_text(json_text)
        print(f"Report saved to {save_path}", file=sys.stderr)

    if args.html:
        HTML_REPORT_PATH.write_text(generate_html(local_report))
        print(f"HTML report saved to {HTML_REPORT_PATH}", file=sys.stderr)

    # Always emit JSON to stdout.
    print(json_text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
