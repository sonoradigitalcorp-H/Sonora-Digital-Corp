#!/usr/bin/env python3
"""
SDC Preflight — Validación completa del ecosistema antes de desarrollar.

Uso:
    python3 scripts/preflight.py                         # solo diagnosticar
    python3 scripts/preflight.py --fix                   # auto-corregir lo posible
    python3 scripts/preflight.py --json                  # salida JSON
    python3 scripts/preflight.py --skip-docker           # saltar checks de Docker
    python3 scripts/preflight.py --skip-git              # saltar checks de git

Salida:
    Códigos de color + ✓/⚠/✗ para cada check.
    Exit code: 0 = todo bien, 1 = warnings, 2 = errores bloqueantes.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple


# ── Colores ANSI ──────────────────────────────────────────────────────────

class C:
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"


# ── Helpers ───────────────────────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_SUMMARY: Dict[str, Any] = {"passed": 0, "warnings": 0, "errors": 0, "fixed": 0}
_KNOWN_OPCODE_V1_KEYS = frozenset({
    "apiKey", "fallbackProvider", "models", "skillsDir", "agentsDir",
    "projectContext", "provider", "model", "shell", "logLevel",
})
_OPCODE_V2_ONLY_KEYS = frozenset({
    "model", "$schema", "shell", "logLevel",
})
_OPCODE_V2_DEPRECATED = frozenset({
    "apiKey", "fallbackProvider",
})
_VALID_OPCODE_MODEL_PREFIXES = (
    "openrouter/", "opencode/", "anthropic/", "openai/", "google/",
)


def _run(cmd: List[str], timeout: int = 15) -> Tuple[int, str, str]:
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return p.returncode, p.stdout.strip(), p.stderr.strip()
    except FileNotFoundError:
        return 127, "", "command not found"
    except subprocess.TimeoutExpired:
        return 124, "", "timed out"


def _which(name: str) -> Optional[str]:
    return shutil.which(name)


def _ok(text: str, detail: str = "") -> None:
    print(f"  {C.GREEN}✓{C.RESET} {text}" + (f" {C.DIM}{detail}{C.RESET}" if detail else ""))
    _SUMMARY["passed"] += 1


def _warn(text: str, detail: str = "") -> None:
    print(f"  {C.YELLOW}⚠{C.RESET} {text}" + (f" {C.DIM}{detail}{C.RESET}" if detail else ""))
    _SUMMARY["warnings"] += 1


def _fail(text: str, detail: str = "") -> None:
    print(f"  {C.RED}✗{C.RESET} {text}" + (f" {C.DIM}{detail}{C.RESET}" if detail else ""))
    _SUMMARY["errors"] += 1


def _fix(text: str, detail: str = "") -> None:
    print(f"  {C.GREEN}🔧{C.RESET} {text}" + (f" {C.DIM}{detail}{C.RESET}" if detail else ""))
    _SUMMARY["fixed"] += 1


def _section(title: str) -> None:
    print(f"\n{C.BOLD}{C.CYAN}◆ {title}{C.RESET}")


def _check_text(text: str, detail: str = "", status: str = "ok") -> None:
    fn = {"ok": _ok, "warn": _warn, "fail": _fail}.get(status, _ok)
    fn(text, detail)


def _blocked_error(short: str) -> str:
    return f"{C.RED}{C.BOLD}✗ BLOQUEANTE:{C.RESET} {short}"


# ── JSON Validation ────────────────────────────────────────────────────

def _walk_files(root: Path, patterns: Tuple[str, ...]) -> List[Path]:
    """Walk a directory tree, excluding common large/generated dirs."""
    exclude = {"node_modules", ".git", "__pycache__", ".venv", "venv",
               "backups", "archive", ".config", "target", "dist", "build"}
    result = []
    try:
        for dirpath, dirnames, filenames in os.walk(root):
            dp = Path(dirpath)
            rel = dp.relative_to(root)
            parts = set(rel.parts) if rel != Path(".") else set()
            if parts & exclude:
                dirnames.clear()
                continue
            # Prune excluded dirs in-place so os.walk doesn't descend
            dirnames[:] = [d for d in dirnames if d not in exclude]
            for fn in filenames:
                if fn.endswith(patterns):
                    result.append(dp / fn)
    except PermissionError:
        pass
    return sorted(result)


def validate_json_files(root: Path, fix: bool) -> None:
    _section("JSON Syntax")

    exclude_pattern = re.compile(r"(package-lock|\.chunk)\.json$")
    json_files = _walk_files(root, (".json", ".jsonc"))

    errors = 0
    fixed = 0
    skipped = 0

    for f in json_files:
        if exclude_pattern.search(f.name):
            skipped += 1
            continue
        rel = f.relative_to(root)
        try:
            text = f.read_text(encoding="utf-8")
            is_template = "{{" in text or "{%" in text
            if f.suffix == ".jsonc":
                # jsonc allows trailing commas — strip them
                stripped = re.sub(r",\s*([}\]])", r"\1", text)
                json.loads(stripped)
            else:
                json.loads(text)
            if is_template:
                _ok(str(rel), detail="(template)")
            else:
                _ok(str(rel))
        except json.JSONDecodeError as e:
            if is_template:
                _warn(f"{rel}: template vars (not valid JSON standalone)")
            elif fix:
                if _try_fix_json(f):
                    _fix(f"Fixed {rel}")
                    fixed += 1
                else:
                    _fail(f"{rel}: {e}")
                    errors += 1
            else:
                _fail(f"{rel}: {e}")
                errors += 1

    if skipped:
        print(f"   {C.DIM}({skipped} archivos excluidos){C.RESET}")


def _try_fix_json(path: Path) -> bool:
    """Intenta reparar un JSON mal formado."""
    text = path.read_text(encoding="utf-8")
    # Eliminar comas sobrantes
    text = re.sub(r",\s*([}\]])", r"\1", text)
    # Eliminar llaves duplicadas al final
    lines = text.splitlines()
    cleaned = []
    brace_count = 0
    for line in lines:
        brace_count += line.count("{") - line.count("}")
        if brace_count < 0:
            brace_count = 0
            continue
        cleaned.append(line)
    text = "\n".join(cleaned)
    try:
        json.loads(text)
        path.write_text(text)
        return True
    except json.JSONDecodeError:
        return False


# ── OpenCode Config Validation ──────────────────────────────────────────

def validate_opencode_configs(root: Path, fix: bool) -> None:
    _section("OpenCode Config")

    configs = [
        root / "opencode.json",
        root / "skills" / "opencode.jsonc",
    ]

    for cfg in configs:
        if not cfg.exists():
            _warn(f"{cfg.relative_to(root)} not found", "(skipping)")
            continue

        rel = cfg.relative_to(root)
        try:
            text = cfg.read_text(encoding="utf-8")
            data = json.loads(text)
        except json.JSONDecodeError as e:
            _fail(f"{rel}: invalid JSON", str(e))
            continue

        # Check for deprecated keys
        for key in _OPCODE_V2_DEPRECATED:
            if key in data:
                _warn(f"{rel}: deprecated key '{key}'", "remove it for compatibility")
                if fix:
                    del data[key]
                    cfg.write_text(json.dumps(data, indent=2) + "\n")
                    _fix(f"{rel}: removed deprecated key '{key}'")

        # Check for unrecognized keys (v1 keys not in v2)
        unrecognized = {k for k in data if k not in _OPCODE_V2_ONLY_KEYS
                        and k not in _OPCODE_V2_DEPRECATED
                        and k not in ("username", "instructions", "agent",
                                      "default_agent", "provider")}
        if unrecognized:
            _warn(f"{rel}: unrecognized keys", ", ".join(sorted(unrecognized)))

        # Check model field
        model = data.get("model", "")
        if not model:
            _fail(f"{rel}: no 'model' field set")
        elif not any(model.startswith(p) for p in _VALID_OPCODE_MODEL_PREFIXES):
            _warn(f"{rel}: model '{model}' may not be valid",
                  "expected prefix: openrouter/, opencode/, anthropic/, openai/, google/")

        # Check for stale instructions paths
        instructions = data.get("instructions", [])
        for inst in instructions:
            if inst.startswith("/home/mystic/"):
                _warn(f"{rel}: hardcoded absolute path in instructions",
                      f"'{inst}' — use relative paths for portability")


# ── YAML Validation ─────────────────────────────────────────────────────

def validate_yaml_files(root: Path, fix: bool) -> None:
    _section("YAML Syntax")
    try:
        import yaml
    except ImportError:
        _warn("PyYAML not installed", "install with: pip install pyyaml")
        return

    yaml_files = _walk_files(root, (".yaml", ".yml"))
    count = 0
    template_warnings = 0
    for f in yaml_files:
        rel = f.relative_to(root)
        text = f.read_text(encoding="utf-8")
        # Check if it's a template with Jinja2/variable syntax
        is_template = "{{" in text or "{%" in text
        try:
            yaml.safe_load(text)
            _ok(str(rel))
            count += 1
        except yaml.YAMLError as e:
            if is_template:
                _warn(f"{rel}: template vars (not valid YAML standalone)", detail=str(e).splitlines()[0] if str(e) else "")
                template_warnings += 1
            else:
                _fail(f"{rel}: {e}")

    if count == 0:
        _warn("No YAML files found")


# ── Docker Health ───────────────────────────────────────────────────────

def validate_docker(root: Path, fix: bool) -> None:
    _section("Docker")
    if not _which("docker"):
        _warn("docker not installed in PATH")
        return

    code, out, err = _run(["docker", "info", "--format", "{{.ServerVersion}}"])
    if code != 0:
        _fail("Docker daemon not running", err or "is docker running?")
        if fix:
            _run(["sudo", "systemctl", "start", "docker"])
            code2, _, _ = _run(["docker", "info"])
            if code2 == 0:
                _fix("Docker daemon started")
            else:
                _warn("Could not start Docker automatically")
        return

    _ok(f"Docker daemon v{out}")

    # Check expected containers
    compose_path = root / "infra" / "docker-compose.yml"
    if compose_path.exists():
        code, out, _ = _run(["docker", "compose", "-f", str(compose_path), "ps", "--format", "json"])
        if code == 0 and out:
            containers = [json.loads(line) for line in out.splitlines() if line.strip()]
            unhealthy = [c.get("Name", "?") for c in containers
                         if c.get("Health", "") == "unhealthy"
                         or c.get("State", "") != "running"]
            if unhealthy:
                _warn(f"Unhealthy containers: {', '.join(unhealthy)}")
                if fix:
                    for name in unhealthy:
                        _run(["docker", "restart", name])
                        _fix(f"Restarted {name}")
            else:
                _ok(f"All {len(containers)} containers healthy")
        elif code != 0:
            _warn("Could not query containers", err)
        else:
            _warn("No containers running via docker-compose")


# ── Git Health ──────────────────────────────────────────────────────────

def validate_git(root: Path, fix: bool) -> None:
    _section("Git")

    git_dir = root / ".git"
    if not git_dir.exists():
        _fail("Not a git repository")
        return

    _ok("Git repository found")

    # Check dirty files
    code, out, _ = _run(["git", "status", "--porcelain"], timeout=10)
    if code == 0 and out:
        lines = out.splitlines()
        _warn(f"{len(lines)} dirty file(s)", "run 'git status' to review")
    else:
        _ok("Working tree clean")

    # Check branch
    code, branch, _ = _run(["git", "branch", "--show-current"])
    if code == 0 and branch:
        _ok(f"On branch '{branch}'")
        # Check if ahead/behind remote
        code2, tracking, _ = _run(["git", "rev-list", "--left-right", "--count",
                                   f"{branch}@{{upstream}}...{branch}"], timeout=10)
        if code2 == 0 and tracking:
            parts = tracking.split()
            behind = int(parts[0]) if parts else 0
            ahead = int(parts[1]) if len(parts) > 1 else 0
            if behind:
                _warn(f"{behind} commit(s) behind remote", "run 'git pull'")
            if ahead:
                _warn(f"{ahead} commit(s) ahead of remote", "run 'git push'")
            if not behind and not ahead:
                _ok("Up to date with remote")
    else:
        _warn("Detached HEAD or no branch")

    # Check recent commits
    code, log, _ = _run(["git", "log", "--oneline", "-5"], timeout=10)
    if code == 0 and log:
        print(f"   {C.DIM}Recent:{C.RESET}")
        for line in log.splitlines():
            print(f"     {C.DIM}{line}{C.RESET}")


# ── Environment Variables ───────────────────────────────────────────────

def validate_env_vars(root: Path, fix: bool) -> None:
    _section("Environment Variables")

    env_example = root / ".env.example"
    env_file = root / ".env"

    if not env_example.exists():
        _warn(".env.example not found", "create one as a template for required vars")
        return

    _ok(".env.example exists")

    required_vars: List[str] = []
    for line in env_example.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key = line.split("=", 1)[0].strip()
            if key:
                required_vars.append(key)

    if not required_vars:
        _warn(".env.example has no variable definitions")
        return

    # Check which vars are set
    missing = []
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)

    if missing:
        _warn(f"{len(missing)} env var(s) not set", ", ".join(missing[:5])
              + (f" + {len(missing)-5} more" if len(missing) > 5 else ""))
    else:
        _ok(f"All {len(required_vars)} required env vars are set")

    # Check .env file exists
    if env_file.exists():
        _ok(".env file exists")

        # Check for common mistakes
        env_text = env_file.read_text()
        if "#" in env_text:
            # Check if any line has a trailing unquoted '#'
            for i, line in enumerate(env_text.splitlines(), 1):
                stripped = line.strip()
                if stripped and not stripped.startswith("#") and "#" in stripped and "=" in stripped:
                    key = stripped.split("=", 1)[0]
                    val = stripped.split("=", 1)[1]
                    if "#" in val and "'" not in val and '"' not in val:
                        _warn(f".env:{i}: value may contain unquoted comment", f"'{stripped}'")
                        break
    else:
        _warn(".env file missing (create from .env.example)")


# ── File Permissions ────────────────────────────────────────────────────

def validate_permissions(root: Path, fix: bool) -> None:
    _section("File Permissions")

    scripts_dir = root / "scripts"
    if not scripts_dir.exists():
        return

    not_executable = []
    for f in sorted(scripts_dir.iterdir()):
        if f.name.endswith(".py") or f.name.endswith(".sh"):
            if not os.access(f, os.X_OK):
                not_executable.append(f.name)

    if not_executable:
        _warn(f"{len(not_executable)} script(s) not executable")
        if fix:
            for name in not_executable:
                (scripts_dir / name).chmod(0o755)
                _fix(f"chmod +x scripts/{name}")
    else:
        _ok("All scripts executable")


# ── System Info ─────────────────────────────────────────────────────────

def validate_system(root: Path, fix: bool) -> None:
    _section("System")

    # Python version
    py = sys.version_info
    if py >= (3, 10):
        _ok(f"Python {py.major}.{py.minor}.{py.micro}")
    else:
        _fail(f"Python {py.major}.{py.minor}.{py.micro}", "3.10+ required")

    # Disk space
    if platform.system() == "Linux":
        code, out, _ = _run(["df", "-h", str(root)])
        if code == 0:
            for line in out.splitlines():
                parts = line.split()
                if len(parts) >= 5 and parts[5] == str(root) or parts[5] == "/":
                    try:
                        pct = int(parts[4].rstrip("%"))
                        if pct > 85:
                            _warn(f"Disk {pct}% full", f"{parts[1]} total, {parts[3]} free")
                        else:
                            _ok(f"Disk {pct}% used", f"{parts[3]} free")
                    except ValueError:
                        pass

    # Memory
    if platform.system() == "Linux":
        try:
            meminfo = Path("/proc/meminfo").read_text()
            for line in meminfo.splitlines():
                if line.startswith("MemAvailable:"):
                    kb = int(line.split()[1])
                    gb = kb / 1024 / 1024
                    _ok(f"RAM: {gb:.1f}GB available")
                    break
        except (FileNotFoundError, ValueError, IndexError):
            pass


# ── OpenCode Compatibility Check ────────────────────────────────────────

def check_opencode_compatibility(root: Path, fix: bool) -> None:
    _section("OpenCode CLI")
    code, version, err = _run(["opencode", "--version"])
    if code != 0:
        _warn("OpenCode CLI not found in PATH", "install with: npm install -g opencode")
        return

    _ok(f"OpenCode CLI v{version}")

    # Parse version
    ver_match = re.match(r"(\d+)\.(\d+)\.(\d+)", version)
    if not ver_match:
        _warn(f"Unknown OpenCode version format: {version}")
        return

    major, minor, patch = int(ver_match[1]), int(ver_match[2]), int(ver_match[3])

    # Check main config compatibility
    cfg_path = root / "opencode.json"
    if not cfg_path.exists():
        _fail("opencode.json not found at project root")
        return

    try:
        cfg_data = json.loads(cfg_path.read_text())
    except json.JSONDecodeError:
        _fail("opencode.json has invalid JSON")
        return

    # Check for v1 keys that break v1.18+
    if major >= 1 and minor >= 18:
        v1_keys_found = [k for k in cfg_data if k in _OPCODE_V2_DEPRECATED]
        if v1_keys_found:
            _fail(f"Config incompatible with OpenCode v{version}",
                  f"remove keys: {', '.join(v1_keys_found)}")
            if fix:
                for key in v1_keys_found:
                    del cfg_data[key]
                cfg_path.write_text(json.dumps(cfg_data, indent=2) + "\n")
                _fix(f"Removed incompatible keys from opencode.json")


# ── Main Runner ─────────────────────────────────────────────────────────

def run_preflight(root: Path, args: argparse.Namespace) -> int:
    fix = args.fix

    print(f"\n{C.BOLD}{C.CYAN}┌──────────────────────────────────────┐{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}│     SDC Preflight — Doctor Check      │{C.RESET}")
    print(f"{C.BOLD}{C.CYAN}└──────────────────────────────────────┘{C.RESET}")
    print(f"  {C.DIM}{root}{C.RESET}\n")

    validate_json_files(root, fix)
    validate_opencode_configs(root, fix)
    validate_yaml_files(root, fix)

    if not args.skip_docker:
        validate_docker(root, fix)

    if not args.skip_git:
        validate_git(root, fix)

    validate_env_vars(root, fix)
    validate_permissions(root, fix)
    validate_system(root, fix)
    check_opencode_compatibility(root, fix)

    # ── Summary ────────────────────────────────────────────────────────
    s = _SUMMARY
    print(f"\n{C.BOLD}{'─' * 46}{C.RESET}")
    print(f"  {C.BOLD}Summary:{C.RESET}")
    print(f"    {C.GREEN}✓ Passed:  {s['passed']}{C.RESET}")
    print(f"    {C.YELLOW}⚠ Warnings: {s['warnings']}{C.RESET}")
    print(f"    {C.RED}✗ Errors:  {s['errors']}{C.RESET}")
    if s["fixed"]:
        print(f"    {C.GREEN}🔧 Fixed:   {s['fixed']}{C.RESET}")

    if s["errors"]:
        print(f"\n  {C.RED}{C.BOLD}✗ Some checks failed. Review above.{C.RESET}")
        return 2
    if s["warnings"]:
        print(f"\n  {C.YELLOW}{C.BOLD}⚠ All critical checks passed.{C.RESET}")
        return 1
    print(f"\n  {C.GREEN}{C.BOLD}✓ All checks passed.{C.RESET}")
    return 0


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="SDC Preflight — validate project config, JSON, Docker, git, and env before developing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python3 scripts/preflight.py
              python3 scripts/preflight.py --fix
              python3 scripts/preflight.py --json
              python3 scripts/preflight.py --skip-docker
        """),
    )
    p.add_argument("--fix", action="store_true", help="Auto-fix issues when possible")
    p.add_argument("--json", action="store_true", help="Output machine-readable JSON")
    p.add_argument("--skip-docker", action="store_true", help="Skip Docker checks")
    p.add_argument("--skip-git", action="store_true", help="Skip Git checks")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.json:
        # Not fully implemented for JSON mode; show info and run normally for now
        pass

    root = _PROJECT_ROOT
    return run_preflight(root, args)


if __name__ == "__main__":
    sys.exit(main())
