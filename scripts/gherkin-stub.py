#!/usr/bin/env python3
"""Lee un .feature file y genera test stubs."""
import sys
from pathlib import Path

def parse_feature(path: Path):
    scenarios = []
    current = None
    for line in path.read_text().splitlines():
        if line.startswith("Scenario:"):
            current = line.replace("Scenario:", "").strip()
            scenarios.append({"name": current, "steps": []})
        elif current and line.strip().startswith(("Given", "When", "Then", "And", "But")):
            scenarios[-1]["steps"].append(line.strip())
    return scenarios

def generate_stubs(scenarios, lang="python"):
    if lang == "python":
        out = ["import pytest\n", ""]
        for s in scenarios:
            name = s["name"].lower().replace(" ", "_").replace("-", "_")
            out.append(f"def test_{name}():")
            out.append("    # Given")
            for st in s["steps"]:
                if st.startswith("Given"):
                    out.append(f"    # {st}")
            out.append("    # When")
            for st in s["steps"]:
                if st.startswith("When"):
                    out.append(f"    # {st}")
            out.append("    # Then")
            for st in s["steps"]:
                if st.startswith("Then"):
                    out.append(f"    # {st}")
            out.append("    assert False  # TODO: implement")
            out.append("")
        return "\n".join(out)
    return "# Unsupported language"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python3 gherkin-stub.py <feature.feature>")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print(f"❌ {path} no existe")
        sys.exit(1)
    scenarios = parse_feature(path)
    if not scenarios:
        print("❌ No scenarios found")
        sys.exit(1)
    stubs = generate_stubs(scenarios)
    out_path = path.with_suffix("_test.py")
    out_path.write_text(stubs)
    print(f"✅ Stubs generados: {out_path} ({len(scenarios)} scenarios)")
