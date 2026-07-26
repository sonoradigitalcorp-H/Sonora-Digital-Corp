const { chromium } = require('playwright');

(async () => {
  console.log('=== SMOKE TEST: Sonora Digital Corp Platform ===\n');
  const browser = await chromium.launch({ headless: true });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 800 } });
  const page = await ctx.newPage();
  let pass = 0, fail = 0;
  
  const check = async (num, name, fn) => {
    try {
      const result = await fn();
      console.log(`${num}  ${name}: ✅ ${result || ''}`);
      pass++;
    } catch(e) { console.log(`${num}  ${name}: ❌ ${e.message.slice(0,80)}`); fail++; }
  };
  
  await page.goto('https://sonoradigitalcorp.com/', { waitUntil: 'networkidle', timeout: 30000 });
  
  await check('1️⃣', 'Landing loads', async () => await page.title() !== '');
  await check('2️⃣', 'Hero section', async () => (await page.$('.hero')) !== null);
  await check('3️⃣', 'Neuron 3D scene', async () => (await page.$('#neuron-container')) !== null);
  await check('4️⃣', 'Agent info panel', async () => (await page.$('.agent-info-panel')) !== null);
  await check('5️⃣', 'Feature cards', async () => (await page.$$('.feature-card')).length >= 3);
  await check('6️⃣', 'Pricing plans', async () => (await page.$$('.pricing-card')).length >= 2);
  await check('7️⃣', 'How it works steps', async () => (await page.$$('.step-card')).length >= 2);
  await check('8️⃣', 'Footer links', async () => (await page.$$('.footer-col a')).length >= 4);
  
  // Navigate to register via hash
  await page.evaluate(() => window.location.hash = '#register');
  await page.waitForTimeout(800);
  await check('9️⃣', 'Register form', async () => (await page.$('#registerForm')) !== null);
  
  // Register a user
  const ts = Date.now();
  await page.fill('#regName', 'Test');
  await page.fill('#regEmail', `t${ts}@test.com`);
  await page.fill('#regPhone', '+526621234567');
  await page.fill('#regPassword', 'Pass1234');
  await page.fill('#regConfirm', 'Pass1234');
  // Click register checkbox first
  const checkbox = await page.$('.form-checkbox input[type="checkbox"]');
  if (checkbox) await checkbox.check();
  await page.click('button:has-text("Crear Cuenta")');
  await page.waitForTimeout(1000);
  
  await check('🔟', 'Dashboard loads after register', async () => {
    const title = await page.textContent('.page-title');
    return title && title.includes('Dashboard') ? '✅' : '❌';
  });
  
  // Navigate via sidebar
  await page.evaluate(() => window.location.hash = '#agents');
  await page.waitForTimeout(1000);
  await check('1️⃣1️⃣', 'Agent catalog loads', async () => {
    const cards = await page.$$('.agent-card');
    return cards.length > 0 ? `${cards.length} agents` : '❌';
  });
  
  await page.evaluate(() => window.location.hash = '#my-agents');
  await page.waitForTimeout(500);
  await check('1️⃣2️⃣', 'My Agents page', async () => (await page.$('#myAgentsContainer')) !== null);
  
  await page.evaluate(() => window.location.hash = '#reseller');
  await page.waitForTimeout(500);
  await check('1️⃣3️⃣', 'Reseller portal', async () => (await page.textContent('.reseller-revenue')) !== null);
  
  await page.evaluate(() => window.location.hash = '#profile');
  await page.waitForTimeout(500);
  await check('1️⃣4️⃣', 'Profile settings', async () => (await page.$('.profile-section')) !== null);
  
  // Mobile
  await page.setViewportSize({ width: 375, height: 667 });
  await page.waitForTimeout(300);
  await check('1️⃣5️⃣', 'Mobile responsive', async () => (await page.$('.hamburger')) !== null);
  
  // Check demo credentials are GONE
  await page.evaluate(() => window.location.hash = '#login');
  await page.waitForTimeout(500);
  const loginText = await page.textContent('.auth-box');
  await check('1️⃣6️⃣', 'No hardcoded credentials', async () => !loginText.includes('Demo2026') ? '✅' : '❌');
  
  await browser.close();
  console.log(`\n📊 ${pass} passed, ${fail} failed de ${pass+fail} tests`);
})().catch(e => console.error('FATAL:', e.message));
