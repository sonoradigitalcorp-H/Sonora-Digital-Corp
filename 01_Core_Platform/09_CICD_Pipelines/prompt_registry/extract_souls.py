"""Extract the canonical SOULS dict from vps_ai_server.py into souls.py for the eval."""
import ast
import re

src_path = "/opt/hermes/vps_ai_server.py"
out_path = "/opt/hermes/prompt_registry/souls.py"

with open(src_path) as f:
    content = f.read()

# Find SOULS = { ... } and parse via ast
m = re.search(r"SOULS\s*=\s*(\{.*?\n\})", content, re.S)
if not m:
    print("No encontre SOULS")
    raise SystemExit(1)

try:
    souls = ast.literal_eval(m.group(1))
except Exception as e:
    # Valores son tuplas de strings concatenadas -> evaluar como dict
    ns = {}
    exec("SOULS = " + m.group(1), ns)
    souls = ns["SOULS"]

with open(out_path, "w") as f:
    f.write("# souls.py — SOULS canónicos extraídos de vps_ai_server.py (producción)\n")
    f.write("# Generado por extract_souls.py. NO editar a mano.\n\n")
    f.write("SOULS = {\n")
    for k, v in souls.items():
        text = v if isinstance(v, str) else str(v)
        f.write(f'    "{k}": {text!r},\n')
    f.write("}\n")

print(f"Extraidos {len(souls)} souls a {out_path}")
for k in souls:
    print(f"  - {k}: {len(souls[k])} chars")
