#!/usr/bin/env python3
"""
Behavior Analyzer — Analiza patrones de trabajo y propone automatizaciones

Analiza: commits, logs de sesión, errores frecuentes, tareas repetitivas
Output: Reporte de comportamiento + propuestas de automatización
"""
import json
import os
import subprocess
import re
from pathlib import Path
from datetime import datetime, timedelta
from collections import Counter, defaultdict

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / 'memory' / 'behavior-log.md'
ERROR_FILE = BASE_DIR / 'DOCUMENTO_DE_ERRORES.md'

ANALYSIS_TEMPLATE = """# Self-Analysis Report
## {date}

### Productividad: {productivity}/10

### Patrones Eficientes ✅
{good_patterns}

### Patrones a Mejorar ❌
{bad_patterns}

### Automatizaciones Propuestas
{automations}

### Score de Automatización: {automation_score}/100

### Detalle de Sesión
{session_detail}
"""

def run_git_log(days=7):
    """Get recent commits for pattern analysis"""
    since = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    try:
        result = subprocess.run(
            ['git', 'log', f'--since={since}', '--oneline', '--no-decorate'],
            capture_output=True, text=True, timeout=15,
            cwd=BASE_DIR
        )
        return result.stdout.strip().split('\n') if result.stdout.strip() else []
    except:
        return []

def analyze_commits(commits):
    """Analyze commit patterns"""
    patterns = defaultdict(list)
    for c in commits:
        parts = c.split(' ', 1)
        if len(parts) == 2:
            msg = parts[1].lower()
            if any(w in msg for w in ['fix', 'bug', 'error', 'hotfix']):
                patterns['fixes'].append(c)
            elif any(w in msg for w in ['add', 'new', 'create', 'feature']):
                patterns['features'].append(c)
            elif any(w in msg for w in ['test', 'spec']):
                patterns['tests'].append(c)
            elif any(w in msg for w in ['refactor', 'clean', 'rename', 'move']):
                patterns['refactors'].append(c)
            elif any(w in msg for w in ['deploy', 'release', 'version']):
                patterns['deploys'].append(c)
            else:
                patterns['other'].append(c)
    return patterns

def analyze_errors():
    """Analyze error document for patterns"""
    if not ERROR_FILE.exists():
        return Counter()
    text = ERROR_FILE.read_text()
    # Count error categories
    categories = re.findall(r'## (\w+)', text)
    return Counter(categories)

def detect_repeated_tasks(patterns):
    """Detect tasks done more than 3 times"""
    repeated = []
    count = Counter()
    for cat, items in patterns.items():
        for item in items:
            # Extract meaningful words from commit messages
            words = item.lower().split()[1:] if len(item.split()) > 1 else []
            for w in words:
                if len(w) > 4:
                    count[w] += 1
    
    for word, freq in count.most_common(10):
        if freq >= 3:
            repeated.append((word, freq))
    return repeated

def suggest_automation(task_word, frequency):
    """Suggest automation for repeated patterns"""
    suggestions = {
        'prompt': lambda f: f"Crear/actualizar prompt para generar esto automáticamente (freq: {f})",
        'script': lambda f: f"Convertir en script reusable (freq: {f})",
        'test': lambda f: f"Automatizar con test suite (freq: {f})",
        'deploy': lambda f: f"Crear pipeline CI/CD (freq: {f})",
        'fix': lambda f: f"Crear regla de linter o pre-commit hook (freq: {f})",
        'refactor': lambda f: f"Establecer standard pattern para evitar refactors repetitivos (freq: {f})",
        'config': lambda f: f"Mover a .env + template (freq: {f})",
        'clean': lambda f: f"Agregar cleanup automático a la rutina diaria (freq: {f})",
        'update': lambda f: f"Crear script de update automático (freq: {f})",
    }
    for key, sugg in suggestions.items():
        if key in task_word:
            return sugg(frequency)
    return f"Revisar si '{task_word}' (x{frequency}) se puede automatizar"

def calculate_automation_score(patterns):
    """Calculate how much of the work is automated"""
    total = sum(len(v) for v in patterns.values())
    if total == 0:
        return 50
    # Count automated-friendly tasks (tests, deploys that should be auto)
    automated = len(patterns.get('tests', [])) + len(patterns.get('deploys', []))
    return min(100, int(automated / max(total, 1) * 100))

def calculate_productivity(patterns):
    """Estimate productivity score"""
    total = sum(len(v) for v in patterns.values())
    if total == 0:
        return 7
    # Features + tests = good, Fixes + refactors = neutral, Other = bad signal
    good = len(patterns.get('features', [])) + len(patterns.get('tests', []))
    neutral = len(patterns.get('fixes', [])) + len(patterns.get('refactors', []))
    bad = len(patterns.get('other', []))
    score = min(10, max(3, int((good * 2 + neutral) / (total + 1) * 5)))
    return score

def get_ram_status():
    try:
        free = subprocess.run(['free', '-m'], capture_output=True, text=True, timeout=5)
        for line in free.stdout.split('\n'):
            if 'Mem:' in line:
                parts = line.split()
                return f"{int(parts[6])}MB libre de {int(parts[1])}MB"
    except:
        return "desconocido"
    return "desconocido"

def get_docker_status():
    try:
        ps = subprocess.run(['docker', 'ps', '--format', '{{.Names}}'], capture_output=True, text=True, timeout=5)
        containers = [c for c in ps.stdout.strip().split('\n') if c]
        return f"{len(containers)} contenedores: {', '.join(containers[:5])}"
    except:
        return "docker no disponible"

def main():
    days = 7
    print(f"🔍 Analyzing behavior for last {days} days...")
    
    commits = run_git_log(days)
    print(f"📝 Found {len(commits)} commits")
    
    patterns = analyze_commits(commits)
    errors = analyze_errors()
    repeated = detect_repeated_tasks(patterns)
    
    automations = []
    for word, freq in repeated:
        suggestion = suggest_automation(word, freq)
        automations.append(f"- '{word}' (x{freq}): {suggestion}")
    
    good = []
    if patterns.get('features'):
        good.append(f"- {len(patterns['features'])} features implementadas")
    if patterns.get('tests'):
        good.append(f"- {len(patterns['tests'])} commits de test")
    if patterns.get('deploys'):
        good.append(f"- {len(patterns['deploys'])} deploys realizados")
    
    bad = []
    if patterns.get('fixes'):
        bad.append(f"- {len(patterns['fixes'])} hotfixes (prevenibles con más tests)")
    if patterns.get('refactors'):
        bad.append(f"- {len(patterns['refactors'])} refactors (señal de diseño inicial débil)")
    if errors:
        bad.append(f"- {sum(errors.values())} errores documentados en {', '.join(errors.keys())}")
    
    productivity = calculate_productivity(patterns)
    automation_score = calculate_automation_score(patterns)
    
    session = [
        f"- RAM: {get_ram_status()}",
        f"- Docker: {get_docker_status()}",
        f"- Commits analizados: {len(commits)}",
        f"- Features: {len(patterns.get('features', []))}",
        f"- Fixes: {len(patterns.get('fixes', []))}",
        f"- Tests: {len(patterns.get('tests', []))}",
    ]
    
    report = ANALYSIS_TEMPLATE.format(
        date=datetime.now().strftime('%Y-%m-%d %H:%M'),
        productivity=productivity,
        good_patterns='\n'.join(good) or 'Ninguno detectado',
        bad_patterns='\n'.join(bad) or 'Ninguno detectado',
        automations='\n'.join(automations) or 'Ninguna automatización necesaria aún',
        automation_score=automation_score,
        session_detail='\n'.join(session)
    )
    
    # Save to file
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LOG_FILE.write_text(report)
    print(f"\n✅ Report saved to {LOG_FILE}")
    print(report)
    
    # Also check if we need to push updates to abe-music.md with new prompts
    gap_analysis()
    
    return report

def gap_analysis():
    """Check what prompts might be missing"""
    prompt_dirs = ['_META', 'IDENTITY', 'AGENTS', 'STRATEGY', 'OPERATIONS', 'CONTENT', 'CODE', 'CLIENTS']
    base = BASE_DIR / 'prompts'
    
    print("\n📋 Gap Analysis — Prompt Coverage:")
    print("=" * 50)
    
    all_expected = {
        '_META': ['meta-generate.md', 'meta-evolve.md', 'meta-audit.md', 'self-analysis.md'],
        'IDENTITY': ['core.md', 'constitution-check.md'],
        'AGENTS': ['executor.md', 'researcher.md', 'communicator.md', 'creator.md', 'operator.md', 'memory.md', 'strategist.md'],
        'STRATEGY': ['business-model.md', 'client-lifecycle.md', 'weekly-review.md', 'delivery-funnel.md'],
        'OPERATIONS': ['daily-routine.md', 'error-response.md', 'resource-management.md', 'client-reporting.md', 'gateway-config.md'],
        'CONTENT': ['landing.md', 'dashboard.md', 'report-html.md'],
        'CODE': ['tdd-cycle.md', 'test-patterns.md', 'agent-harness.md'],
        'CLIENTS': ['abe-music.md', 'template.md', 'delivery-gate.md'],
    }
    
    for d, expected in all_expected.items():
        dir_path = base / d
        existing = set()
        if dir_path.exists():
            existing = {f.name for f in dir_path.iterdir() if f.suffix == '.md'}
        
        missing = []
        for f in expected:
            if f not in existing:
                missing.append(f)
        
        if missing:
            print(f"  ❌ {d}/ missing: {', '.join(missing)}")
        else:
            print(f"  ✅ {d}/ complete ({len(existing)} files)")

if __name__ == '__main__':
    main()
