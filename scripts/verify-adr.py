#!/usr/bin/env python3
"""ADR/Spec Verification System — valida contenido, compliance, y cobertura de tests (HAS-009)

Usage:
  python3 scripts/verify-adr.py --all
  python3 scripts/verify-adr.py --adr process/active/ADR-20260703-A.md
  python3 scripts/verify-adr.py --spec-coverage
  python3 scripts/verify-adr.py --spec process/active/SPEC-20260712-SONORA-001.md
  python3 scripts/verify-adr.py --compliance process/active/ADR-20260703-A.md
  python3 scripts/verify-adr.py --json
"""

import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)

REPO = Path(__file__).resolve().parent.parent
ADR_DIRS = [REPO / "process" / "active", REPO / "adrs"]
SPEC_DIR = REPO / "process" / "active"
TEST_DIR = REPO / "tests"

ADR_ID_PATTERN = re.compile(r"ADR-\d{8}-[A-Z0-9-]+")
FR_PATTERN = re.compile(r"FR(\d+)")
SPEC_ID_PATTERN = re.compile(r"SPEC-\d{8}-[A-Z0-9-]+")

SECTION_MAP = {
    "context": ["Contexto", "Context"],
    "decision": ["Decisión", "Decision", "Decisiones"],
    "consequences": ["Consecuencias", "Consequences"],
    "options_considered": ["Opciones Consideradas", "Options Considered", "Opciones consideradas"],
    "lessons": ["Lecciones", "Lessons"],
}

TABLE_FIELD_MAP = {
    "ID": ["ID"],
    "Fecha": ["Fecha"],
    "Estado": ["Estado", "Status"],
    "Spec": ["Spec"],
}


def _read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        logger.error("Cannot read %s: %s", path, e)
        return ""


def _parse_yaml_frontmatter(content: str) -> dict[str, str]:
    import yaml
    m = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    try:
        data = yaml.safe_load(m.group(1))
        if isinstance(data, dict):
            return {k: str(v) for k, v in data.items() if v is not None}
    except Exception:
        pass
    return {}


def _find_adr_id(content: str, filepath: Path) -> str:
    m = ADR_ID_PATTERN.search(content)
    if m:
        return m.group(0)
    m = ADR_ID_PATTERN.search(filepath.stem)
    if m:
        return m.group(0)
    return filepath.stem


def _has_section(content: str, names: list[str]) -> bool:
    for name in names:
        if re.search(r"^##\s+" + re.escape(name) + r"\s*$", content, re.MULTILINE):
            return True
    return False


def validate_adr_content(filepath: str) -> dict[str, Any]:
    path = Path(filepath)
    content = _read_file(path)
    if not content:
        return {"valid": False, "errors": ["File empty or unreadable"], "score": 0, "field_checks": {}}

    field_checks: dict[str, bool] = {}

    for field, alternatives in TABLE_FIELD_MAP.items():
        found = False
        for alt in alternatives:
            pat = re.compile(r"(?:\*\*)?" + re.escape(alt) + r"(?:\*\*)?\s*\|\s*(.+)")
            if pat.search(content):
                found = True
                break
        field_checks[field] = found

    yaml_fields = _parse_yaml_frontmatter(content)
    if yaml_fields:
        front_mapping = {"id": "ID", "date": "Fecha", "status": "Estado"}
        for ykey, tkey in front_mapping.items():
            if ykey in yaml_fields and yaml_fields[ykey]:
                field_checks[tkey] = True

    for section_key, names in SECTION_MAP.items():
        field_checks[f"section_{section_key}"] = _has_section(content, names)

    errors: list[str] = []
    for field, found in field_checks.items():
        if not found:
            clean = field.replace("section_", "")
            errors.append(f"Missing: {clean}")

    present = sum(1 for v in field_checks.values() if v)
    total = len(field_checks)
    score = int((present / total) * 100) if total > 0 else 0

    adr_id = _find_adr_id(content, path)

    return {
        "valid": len(errors) == 0,
        "adr_id": adr_id,
        "errors": errors,
        "score": score,
        "field_checks": field_checks,
    }


def validate_adr_compliance(adr_file: str, codebase_dir: str = ".") -> dict[str, Any]:
    path = Path(adr_file)
    content = _read_file(path)
    if not content:
        return {"adr_id": "unknown", "compliant": False, "evidence": [], "violations": ["Cannot read ADR file"]}

    adr_id = _find_adr_id(content, path)
    codebase = Path(codebase_dir)

    keywords = _extract_keywords(content)
    evidence: list[str] = []
    violations: list[str] = []

    for kw in keywords:
        pattern = re.compile(re.escape(kw), re.IGNORECASE)
        matches: list[str] = []
        for ext in ("*.py", "*.yaml", "*.yml", "*.json", "*.md", "*.sql", "*.ts", "*.js"):
            for f in codebase.rglob(ext):
                if ".git" in f.parts or "__pycache__" in f.parts or "node_modules" in f.parts:
                    continue
                try:
                    fcontent = f.read_text(encoding="utf-8", errors="ignore")
                    if pattern.search(fcontent):
                        rel = f.relative_to(codebase)
                        matches.append(str(rel))
                except Exception:
                    continue

        if matches:
            evidence.append(f"'{kw}' found in {len(matches)} files: {', '.join(matches[:5])}")
        else:
            violations.append(f"Keyword '{kw}' not found in codebase")

    return {
        "adr_id": adr_id,
        "compliant": len(violations) == 0,
        "evidence": evidence[:20],
        "violations": violations[:20],
    }


def _extract_keywords(content: str) -> list[str]:
    keywords: list[str] = []
    for line in content.split("\n"):
        m = re.search(r"`([^`]+)`", line)
        if m:
            keyword = m.group(1).strip()
            if len(keyword) > 3 and keyword not in keywords:
                keywords.append(keyword)
    return keywords[:10]


def validate_spec_coverage(spec_file: str) -> dict[str, Any]:
    path = Path(spec_file)
    content = _read_file(path)
    if not content:
        return {"spec_id": "unknown", "frs": {}, "total": 0, "covered": 0}

    spec_id = SPEC_ID_PATTERN.search(content)
    spec_id_val = spec_id.group(0) if spec_id else path.stem

    frs: dict[str, str] = {}
    lines = content.split("\n")
    in_fr_section = False
    for i, line in enumerate(lines):
        if re.search(r"^##\s+3\.?\s*Functional Requirements", line, re.IGNORECASE):
            in_fr_section = True
            continue
        if in_fr_section:
            if re.search(r"^##\s+\d+\.", line):
                in_fr_section = False
                continue
            m = re.match(r"\|?\s*(FR\d+)\s*\|", line)
            if m:
                desc = ""
                for j in range(i, min(i + 3, len(lines))):
                    parts = lines[j].split("|")
                    if len(parts) >= 3:
                        desc = parts[2].strip()
                        break
                frs[m.group(1)] = desc

    results: dict[str, Any] = {}
    covered_count = 0

    gherkin_dir = REPO / "process" / "active" / "gherkin"
    gherkin_file = gherkin_dir / f"{spec_id_val}.feature"
    gherkin_content = _read_file(gherkin_file) if gherkin_file.exists() else ""

    for fr_id in frs:
        tests_found: list[dict[str, str]] = []

        fr_tag = f"@{fr_id.lower()}"
        if fr_tag in gherkin_content:
            for m in re.finditer(
                rf"@{fr_id.lower()}\s*\n\s*Scenario:\s*(.+)",
                gherkin_content, re.IGNORECASE,
            ):
                tests_found.append({
                    "test_file": f"process/active/gherkin/{spec_id_val}.feature",
                    "test_name": m.group(1).strip(),
                })

        fr_ref_pattern = re.compile(re.escape(fr_id), re.IGNORECASE)
        for f in sorted(TEST_DIR.rglob("*.py")):
            if "__pycache__" in f.parts:
                continue
            try:
                fcontent = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if fr_ref_pattern.search(fcontent):
                test_names = re.findall(r"def (test_\w+)", fcontent)
                rel = f.relative_to(REPO)
                for tn in test_names[:3]:
                    tests_found.append({"test_file": str(rel), "test_name": tn})

        covered = len(tests_found) > 0
        if covered:
            covered_count += 1

        results[fr_id] = {
            "covered": covered,
            "description": frs[fr_id],
            "tests": tests_found[:5],
        }

    return {
        "spec_id": spec_id_val,
        "frs": results,
        "total": len(frs),
        "covered": covered_count,
    }


def validate_all_adrs(adr_dir: str | None = None) -> dict[str, Any]:
    if adr_dir:
        targets = [Path(adr_dir)]
    else:
        targets = ADR_DIRS

    results: dict[str, Any] = {}
    total = 0
    valid = 0
    total_score = 0

    for target in targets:
        if not target.exists():
            continue
        for f in sorted(target.glob("ADR-*.md")):
            result = validate_adr_content(str(f))
            adr_id = result["adr_id"]
            results[adr_id] = result
            total += 1
            if result["valid"]:
                valid += 1
            total_score += result["score"]

    return {
        "results": results,
        "total": total,
        "valid": valid,
        "invalid": total - valid,
        "average_score": round(total_score / total, 1) if total > 0 else 0,
    }


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="ADR/Spec Verification System (HAS-009)")
    parser.add_argument("--adr", help="Validate a single ADR file")
    parser.add_argument("--all", action="store_true", help="Validate all ADRs")
    parser.add_argument("--spec", help="Validate spec coverage for a single SPEC file")
    parser.add_argument("--spec-coverage", action="store_true", help="Validate coverage for all SPECs")
    parser.add_argument("--compliance", help="Check ADR compliance against codebase")
    parser.add_argument("--codebase", default=str(REPO), help="Codebase root for compliance check")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    output: dict[str, Any] = {}

    if args.adr:
        output = validate_adr_content(args.adr)
    elif args.spec:
        output = validate_spec_coverage(args.spec)
    elif args.spec_coverage:
        specs = sorted(SPEC_DIR.glob("SPEC-*.md"))
        results: dict[str, Any] = {}
        total_frs = 0
        total_covered = 0
        for s in specs:
            cov = validate_spec_coverage(str(s))
            results[cov["spec_id"]] = cov
            total_frs += cov["total"]
            total_covered += cov["covered"]
        output = {
            "results": results,
            "total_specs": len(specs),
            "total_frs": total_frs,
            "total_covered": total_covered,
            "coverage_pct": round((total_covered / total_frs) * 100, 1) if total_frs > 0 else 0,
        }
    elif args.compliance:
        output = validate_adr_compliance(args.compliance, args.codebase)
    elif args.all:
        output = validate_all_adrs()
    else:
        parser.print_help()
        sys.exit(1)

    if args.json or args.all or args.spec_coverage:
        print(json.dumps(output, indent=2, default=str))
    else:
        _print_human(output)

    if isinstance(output, dict) and output.get("valid") is False and (args.adr or args.compliance):
        sys.exit(1)


def _print_human(result: dict[str, Any]) -> None:
    if "adr_id" in result and "score" in result:
        adr_id = result["adr_id"]
        valid = result.get("valid", False)
        score = result.get("score", 0)
        icon = "✓" if valid else "✗"
        print(f"\n  {icon} {adr_id}: {'VALID' if valid else 'INVALID'} (score: {score}/100)")
        for err in result.get("errors", []):
            print(f"     ✗ {err}")
        for field, found in result.get("field_checks", {}).items():
            ficon = "✓" if found else "✗"
            name = field.replace("section_", "")
            print(f"     {ficon} {name}")
    elif "spec_id" in result and "frs" in result:
        spec_id = result["spec_id"]
        total = result["total"]
        covered = result["covered"]
        pct = round(covered / total * 100, 1) if total else 0
        print(f"\n  SPEC {spec_id}: {covered}/{total} FRs covered ({pct}%)")
        for fr_id, fr_data in sorted(result.get("frs", {}).items()):
            icon = "✓" if fr_data["covered"] else "✗"
            print(f"     {icon} {fr_id}: {fr_data.get('description', '')[:60]}")
            for t in fr_data.get("tests", []):
                print(f"         → {t.get('test_file', '')}::{t.get('test_name', '')}")


if __name__ == "__main__":
    main()
