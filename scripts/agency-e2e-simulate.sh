#!/bin/bash
# AGENCY OS — Playwright User Simulation E2E
# Simula un usuario real abriendo la app en HDMI y navegando
# Ejecuta: Manual o automático en pipeline nocturno
set -euo pipefail

cd /home/mystic/jarvis
export DISPLAY=:0
LOG="logs/playwright-e2e-$(date +%Y%m%d).log"

echo "=== AGENCY OS — Playwright E2E User Simulation ===" | tee "$LOG"
echo "Fecha: $(date)" | tee -a "$LOG"

# Verificar que JARVIS web esté arriba
if ! curl -sf http://localhost:5174 > /dev/null 2>&1; then
    echo "❌ JARVIS web no responde en :5174" | tee -a "$LOG"
    exit 1
fi

# Verificar Playwright instalado
if ! command -v npx &>/dev/null; then
    echo "❌ npx/Playwright no instalado" | tee -a "$LOG"
    exit 1
fi

# === PLAYWRIGHT USER SIMULATION ===
# Abre Chrome en HDMI, navega como usuario real, toma screenshots
SIMULATION=$(cat << 'SCRIPT'
const { chromium } = require('playwright');
const fs = require('fs');
const BASE = 'http://localhost:5174';
const DATE = new Date().toISOString().split('T')[0];
const report = [];

(async () => {
    const browser = await chromium.launch({
        headless: false,
        args: ['--window-position=0,0', '--window-size=1360,768', '--disable-gpu']
    });
    const page = await browser.newPage({ viewport: { width: 1360, height: 768 } });

    // FLUJO 1: Dashboard ABE carga
    console.log('🔄 FLUJO 1: Dashboard ABE');
    await page.goto(`${BASE}/static/dashboard-abe.html`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForSelector('.metric', { timeout: 10000 });
    await page.screenshot({ path: `logs/screenshots/${DATE}-dashboard-abe.png` });
    const title = await page.textContent('header h1');
    report.push({ flow: 'Dashboard ABE', title: title.trim(), status: title.includes('ABE') ? 'OK' : 'FAIL' });
    console.log(`   ✓ Dashboard ABE: "${title.trim()}"`);

    // FLUJO 2: API Dashboard CEO responde
    console.log('🔄 FLUJO 2: API Dashboard CEO');
    const apiResponse = await page.evaluate(async () => {
        const res = await fetch('/api/abe/dashboard/ceo');
        return res.ok ? await res.json() : null;
    });
    report.push({
        flow: 'API Dashboard CEO',
        streams: apiResponse?.total_streams,
        revenue: apiResponse?.total_revenue,
        status: apiResponse?.total_streams > 0 ? 'OK' : 'FAIL'
    });
    console.log(`   ✓ API: ${apiResponse?.total_streams} streams, $${apiResponse?.total_revenue}`);

    // FLUJO 3: ABE Music Hub landing
    console.log('🔄 FLUJO 3: ABE Music Hub');
    await page.goto(`${BASE}/static/abe-music.html`, { waitUntil: 'networkidle', timeout: 15000 });
    await page.waitForTimeout(2000);
    await page.screenshot({ path: `logs/screenshots/${DATE}-abe-hub.png` });
    const hubTitle = await page.textContent('h1');
    report.push({ flow: 'ABE Music Hub', title: hubTitle.trim(), status: hubTitle.includes('HUB') ? 'OK' : 'FAIL' });
    console.log(`   ✓ Hub: "${hubTitle.trim()}"`);

    // FLUJO 4: 100 preguntas (si existe)
    console.log('🔄 FLUJO 4: 100 Preguntas');
    try {
        await page.goto(`${BASE}/static/100-preguntas.html`, { waitUntil: 'networkidle', timeout: 10000 });
        await page.waitForSelector('.q', { timeout: 5000 });
        const questions = await page.$$eval('.q', els => els.length);
        report.push({ flow: '100 Preguntas', questions, status: questions >= 90 ? 'OK' : 'PARTIAL' });
        console.log(`   ✓ ${questions} preguntas cargadas`);
    } catch (e) {
        report.push({ flow: '100 Preguntas', status: 'NOT_FOUND' });
        console.log('   ⚠ No encontrada');
    }

    await browser.close();

    // Report
    console.log('\n=== E2E REPORT ==');
    report.forEach(r => console.log(`${r.status === 'OK' ? '✅' : r.status === 'PARTIAL' ? '⚠️' : '❌'} ${r.flow}: ${r.status}`));
    const passed = report.filter(r => r.status === 'OK').length;
    const total = report.length;
    console.log(`\nResultado: ${passed}/${total} flujos OK`);

    fs.writeFileSync(`logs/e2e-report-${DATE}.json`, JSON.stringify(report, null, 2));
})().catch(e => {
    console.error('❌ E2E Error:', e.message);
    process.exit(1);
});
SCRIPT
)

npx playwright test --headed 2>&1 | tail -5 || node -e "$SIMULATION" 2>&1 | tee -a "$LOG"

echo "=== E2E Complete ===" | tee -a "$LOG"
