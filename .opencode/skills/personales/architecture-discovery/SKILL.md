# Skill: Architecture Discovery

Automatiza el descubrimiento de arquitectura existente en cualquier codebase antes de planificar cambios. Evita el patrón de "escribir código sin saber qué ya existe".

## Cuándo usar
- Antes de crear endpoints, módulos, o procesos nuevos
- Cuando necesitas entender un sistema complejo rápidamente
- Después de un `mem_search` que no arroja resultados

## Patrón (4 herramientas en paralelo)

### 1. `ls` sessions/agents — descubrir datos operativos
```bash
ls -la ~/.openclaw/agents/cesar/sessions/
```
- Busca archivos `.jsonl` (mensajes) y `.trajectory.jsonl` (acciones)
- Ordena por fecha: `sorted(..., key=os.path.getmtime, reverse=True)`

### 2. `grep` patrones de esquema — entender base de datos
```bash
grep -n "CREATE TABLE\|INSERT INTO\|UPDATE.*SET\|column_name\|field" persistence.py
```
- Lee el código fuente del persistence layer en lugar de intentar conectar a DB
- Las columnas reales aparecen en sentencias INSERT/UPDATE

### 3. `find` por feature — localizar componentes
```bash
find 02_Source_Code/Bots/ -name "*.py" | xargs grep -l "class.*Engine\|def.*classify\|def.*persist"
```
- Busca por patrón de funcionalidad, no por nombre de archivo
- Usa: `report|analy|metric|dash|crm|survey|feedback` para discovery de módulos

### 4. `python3` heredoc para JSON inspection
```python
python3 << 'PYEOF'
import json
with open('sessions/latest.jsonl') as f:
    for line in f:
        data = json.loads(line.strip())
        role = data.get('role', '?')
        print(f"[{role}] {data.get('content','')[:150]}")
PYEOF
```
- **SIEMPRE** usar `<< 'PYEOF'` (heredoc) no strings inline
- Evita errores de sintaxis con `.get()` anidado

## PRE-FLIGHT Checklist (antes de crear CUALQUIER cosa)
1. `~/.openclaw/workspace/tenant_registry.json` — ¿el bot ya existe?
2. `ps aux | grep nombreProceso` — ¿el proceso ya corre?
3. `curl -H "Authorization: Bearer KEY" https://openrouter.ai/api/v1/auth/key` — ¿tienes créditos?
4. Busca en `.opencode/skills/` y `01_Core_Platform/` — ¿ya existe un tool/skill?

**Si la respuesta es SÍ a cualquiera → NO crear código. Documentar cómo usar lo existente.**

## Output esperado
- Lista de archivos relevantes con líneas clave
- Esquema de base de datos (columnas detectadas del código)
- Componentes existentes vs faltantes
- Gap analysis: qué ya funciona, qué falta

## Ver también
- `AGENTS.md` — PRE-FLIGHT OBLIGATORIO
- `01_Core_Platform/05_SelfImprovement/` — evaluator + autonomous_loop
