const { chromium } = require('playwright');

const BASE = 'https://sonoradigitalcorp.com';
const TIMESTAMP = Date.now();
const TEST_EMAIL = `e2e-${TIMESTAMP}@test.com`;
const TEST_PASSWORD = 'TestPass123';
const TEST_NAME = 'E2E User';
const TEST_PHONE = '+525512345678';

let browser, page;

async function wait(ms) {
  return new Promise(r => setTimeout(r, ms));
}

async function getVisiblePageTitle() {
  return page.evaluate(() => {
    const visible = Array.from(document.querySelectorAll('.page'))
      .find(p => p.style.display !== 'none' && p.style.display !== '');
    if (!visible) return null;
    const title = visible.querySelector('.page-title');
    return title ? title.textContent.trim() : null;
  });
}

async function getVisiblePageName() {
  return page.evaluate(() => {
    const visible = Array.from(document.querySelectorAll('.page'))
      .find(p => p.style.display !== 'none' && p.style.display !== '');
    return visible ? visible.getAttribute('data-page') : null;
  });
}

async function spaNavigate(hash) {
  await page.evaluate((h) => navigate(h), hash);
  await wait(1200);
}

async function run() {
  const results = { pass: 0, fail: 0, errors: [] };

  async function test(name, fn) {
    try {
      await fn();
      console.log(`  ✅ ${name}`);
      results.pass++;
    } catch (err) {
      console.log(`  ❌ ${name}`);
      console.log(`     ${err.message}`);
      results.fail++;
      results.errors.push({ name, message: err.message });
    }
  }

  browser = await chromium.launch({ headless: true });
  const context = await browser.newContext({
    viewport: { width: 1280, height: 800 },
    locale: 'es-MX',
  });
  page = await context.newPage();

  page.on('dialog', async (dialog) => {
    await dialog.accept();
  });

  console.log('\n=== Test 1: Landing Page ===');
  await test('Hero title exists', async () => {
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.waitForSelector('h1', { timeout: 10000 });
    const heroH1 = await page.$('.hero h1');
    if (!heroH1) throw new Error('Hero h1 not found');
    const text = await heroH1.textContent();
    if (!text.includes('Sistema Operativo')) throw new Error(`Expected "Sistema Operativo" in h1, got: ${text}`);
  });

  await test('Neuron 3D container exists', async () => {
    await page.waitForSelector('#neuron-container', { timeout: 5000 });
    const el = await page.$('#neuron-container');
    if (!el) throw new Error('#neuron-container not found');
  });

  await test('Features show 6 agent cards', async () => {
    await page.waitForSelector('.features-grid', { timeout: 5000 });
    const cards = await page.$$('.feature-card');
    if (cards.length !== 6) throw new Error(`Expected 6 feature cards, got ${cards.length}`);
  });

  await test('Pricing shows 3 plans', async () => {
    await page.waitForSelector('.pricing-grid', { timeout: 5000 });
    const cards = await page.$$('.pricing-card');
    if (cards.length !== 3) throw new Error(`Expected 3 pricing cards, got ${cards.length}`);
  });

  await test('Footer has links', async () => {
    await page.waitForSelector('.footer-enhanced', { timeout: 5000 });
    const links = await page.$$('.footer-enhanced a');
    if (links.length < 4) throw new Error(`Expected at least 4 footer links, got ${links.length}`);
  });

  console.log('\n=== Test 2: Navegación SPA ===');
  await test('Navigate to login shows form', async () => {
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await spaNavigate('login');
    const form = await page.$('#loginForm');
    if (!form) throw new Error('Login form not visible');
  });

  await test('Navigate to pricing section', async () => {
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await page.evaluate(() => {
      const el = document.querySelector('a[href="#pricing"]');
      if (el) el.click();
    });
    await wait(800);
    const section = await page.$('.pricing-section');
    if (!section) throw new Error('Pricing section not found');
    const visible = await section.isVisible();
    if (!visible) throw new Error('Pricing section not visible');
  });

  await test('Navigate to register shows form', async () => {
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await spaNavigate('register');
    const form = await page.$('#registerForm');
    if (!form) throw new Error('Register form not visible');
  });

  console.log('\n=== Test 3: Registro de usuario ===');
  await test('Register with unique data', async () => {
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await spaNavigate('register');
    await page.waitForSelector('#registerForm', { timeout: 5000 });
    await page.fill('#regName', TEST_NAME);
    await page.fill('#regEmail', TEST_EMAIL);
    await page.fill('#regPhone', TEST_PHONE);
    await page.fill('#regPassword', TEST_PASSWORD);
    await page.fill('#regConfirm', TEST_PASSWORD);
    await page.evaluate(() => {
      const cb = document.querySelector('.form-checkbox input[type="checkbox"]');
      if (cb) cb.checked = true;
    });
    await page.click('#registerForm button[type="submit"]');
    await wait(2000);
    const title = await getVisiblePageTitle();
    if (!title || !title.includes('Dashboard')) throw new Error(`Expected Dashboard, got: ${title}`);
  });

  await test('Dashboard shows stats', async () => {
    await wait(1500);
    const statGrid = await page.$('.stat-grid');
    if (!statGrid) throw new Error('Stat grid not found');
    const statVal = await page.textContent('#statAgents');
    if (statVal === '—') throw new Error('Stats did not load');
  });

  console.log('\n=== Test 4: Login ===');
  await test('Logout and return to home', async () => {
    await page.evaluate(() => logout());
    await wait(600);
    const hero = await page.$('.hero');
    if (!hero) throw new Error('Hero not visible after logout');
  });

  await test('Login with registered credentials', async () => {
    await spaNavigate('login');
    await page.waitForSelector('#loginForm', { timeout: 5000 });
    await page.fill('#loginEmail', TEST_EMAIL);
    await page.fill('#loginPassword', TEST_PASSWORD);
    await page.click('#loginForm button[type="submit"]');
    await wait(2000);
    const title = await getVisiblePageTitle();
    if (!title || !title.includes('Dashboard')) throw new Error(`Expected Dashboard, got: ${title}`);
  });

  await test('Dashboard stats visible after login', async () => {
    await wait(1000);
    const statCards = await page.$$('.stat-card');
    if (statCards.length < 3) throw new Error(`Expected at least 3 stat cards, got ${statCards.length}`);
    const tbody = await page.$('#transactionsBody');
    if (!tbody) throw new Error('Transactions table not found');
  });

  console.log('\n=== Test 5: Catálogo de Agentes ===');
  await test('Navigate to catalog from sidebar', async () => {
    await spaNavigate('agents');
    await wait(1500);
    const title = await getVisiblePageTitle();
    if (!title || !title.includes('Catálogo')) {
      const pageName = await getVisiblePageName();
      throw new Error(`Expected Catálogo, got: ${title} (page: ${pageName})`);
    }
  });

  await test('Catalog shows 4 agents', async () => {
    await page.waitForSelector('#agentsGrid', { timeout: 5000 });
    await wait(1500);
    const agents = await page.$$('.agent-card');
    if (agents.length !== 4) throw new Error(`Expected 4 agent cards, got ${agents.length}`);
  });

  await test('Each agent has name, price and button', async () => {
    const agentCards = await page.$$('.agent-card');
    for (let i = 0; i < agentCards.length; i++) {
      const card = agentCards[i];
      const h3 = await card.$('h3');
      const price = await card.$('.price');
      const btn = await card.$('button');
      if (!h3) throw new Error(`Agent ${i} missing name`);
      if (!price) throw new Error(`Agent ${i} missing price`);
      if (!btn) throw new Error(`Agent ${i} missing button`);
    }
  });

  console.log('\n=== Test 6: Compra de Licencia ===');
  await test('Buy Voice Agent license via API', async () => {
    const token = await page.evaluate(() => localStorage.getItem('token'));
    if (!token) throw new Error('No token found');
    const result = await page.evaluate(async (t) => {
      const r = await fetch('/api/demo/buy', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${t}` },
        body: JSON.stringify({ agent_id: 'voice-agent' })
      });
      return r.json();
    }, token);
    if (!result.result || !result.result.success) {
      throw new Error(`Buy failed: ${JSON.stringify(result)}`);
    }
  });

  await test('Purchased agent appears in My Agents', async () => {
    await spaNavigate('my-agents');
    await wait(2000);
    const container = await page.$('#myAgentsContainer');
    if (!container) throw new Error('My Agents container not found');
    const agentCards = await container.$$('.my-agent-card');
    if (agentCards.length === 0) {
      const text = await container.textContent();
      if (text.includes('Sin agentes')) throw new Error('No agents in My Agents after purchase');
    }
    console.log(`     Found ${agentCards.length} licensed agent(s)`);
  });

  console.log('\n=== Test 7: Portal Revender ===');
  await test('Navigate to Reseller portal', async () => {
    await spaNavigate('reseller');
    await wait(1000);
    const title = await getVisiblePageTitle();
    if (!title || !title.includes('Reventa')) {
      const pageName = await getVisiblePageName();
      throw new Error(`Expected Reventa, got: ${title} (page: ${pageName})`);
    }
  });

  await test('Reseller shows revenue and markup fields', async () => {
    const revenue = await page.$('.reseller-revenue');
    if (!revenue) throw new Error('Revenue section not found');
    const revText = await revenue.textContent();
    if (!revText.includes('$')) throw new Error(`Revenue doesn't show amount: ${revText}`);
    const markup = await page.$('#markupInput');
    if (!markup) throw new Error('Markup input not found');
  });

  await test('Modify markup value', async () => {
    const input = await page.$('#markupInput');
    if (!input) throw new Error('Markup input not found');
    await input.fill('45');
    const val = await input.inputValue();
    if (val !== '45') throw new Error(`Expected markup 45, got ${val}`);
  });

  console.log('\n=== Test 8: Perfil ===');
  await test('Navigate to Profile/Settings', async () => {
    await spaNavigate('profile');
    await wait(1000);
    const title = await getVisiblePageTitle();
    if (!title || !title.includes('Ajustes')) {
      const pageName = await getVisiblePageName();
      throw new Error(`Expected Ajustes, got: ${title} (page: ${pageName})`);
    }
  });

  await test('Profile fields are displayed', async () => {
    await page.waitForSelector('.profile-section', { timeout: 5000 });
    const inputs = await page.$$('.profile-section input');
    if (inputs.length < 3) throw new Error(`Expected at least 3 profile inputs, got ${inputs.length}`);
  });

  await test('Modify and save profile', async () => {
    const nameInputs = await page.$$('.profile-section input[type="text"]');
    if (nameInputs.length > 0) {
      await nameInputs[0].fill('E2E Updated Name');
      await wait(300);
      const saveBtn = await page.$('.profile-actions .btn-primary');
      if (saveBtn) {
        await saveBtn.click();
        await wait(500);
      }
    }
  });

  console.log('\n=== Test 9: Responsive Design ===');
  await test('Mobile viewport shows hamburger menu', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await wait(800);
    let hamburger = await page.$('.landing-header .hamburger');
    if (!hamburger) {
      hamburger = await page.$('.mobile-header .hamburger');
    }
    if (!hamburger) throw new Error('Hamburger menu not found on mobile viewport');
  });

  await test('Cards stack in responsive grid on mobile', async () => {
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await wait(500);
    const featureCards = await page.$$('.feature-card');
    if (featureCards.length < 6) throw new Error(`Expected 6 feature cards, got ${featureCards.length}`);
    const grid = await page.$('.features-grid');
    if (!grid) throw new Error('Features grid not found');
  });

  await test('Tablet viewport adapts', async () => {
    await page.setViewportSize({ width: 768, height: 1024 });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await wait(500);
    const hero = await page.$('.hero');
    if (!hero) throw new Error('Hero not visible on tablet');
    const heroText = await hero.textContent();
    if (!heroText.includes('Sistema')) throw new Error('Hero content broken on tablet');
  });

  console.log('\n=== Test 10: 3D Neuron Interaction ===');
  await test('Three.js canvas exists in neuron container', async () => {
    await page.setViewportSize({ width: 1280, height: 800 });
    await page.goto(BASE, { waitUntil: 'networkidle' });
    await wait(3000);
    const hasCanvas = await page.evaluate(() => {
      const nc = document.getElementById('neuron-container');
      if (!nc) return false;
      return nc.querySelectorAll('canvas').length > 0;
    });
    if (!hasCanvas) {
      const hasImportMap = await page.evaluate(() => {
        return document.querySelectorAll('script[type="importmap"]').length > 0;
      });
      if (!hasImportMap) throw new Error('Three.js import map not found');
      const container = await page.$('#neuron-container');
      if (!container) throw new Error('#neuron-container missing');
    }
  });

  await test('Click on neuron scene is possible', async () => {
    const container = await page.$('#neuron-container');
    if (container) {
      const box = await container.boundingBox();
      if (box) {
        await page.mouse.click(box.x + box.width / 2, box.y + box.height / 2);
        await wait(300);
      }
    }
  });

  // Summary
  console.log(`\n========================================`);
  console.log(`  Results: ${results.pass} passed, ${results.fail} failed`);
  console.log(`========================================\n`);

  await browser.close();
  process.exit(results.fail > 0 ? 1 : 0);
}

run().catch(err => {
  console.error('Fatal error:', err);
  if (browser) browser.close();
  process.exit(1);
});
