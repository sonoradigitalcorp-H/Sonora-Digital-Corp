/**
 * Ce-Son v3 — E2E Tests with Playwright
 * 
 * Prereq: API running on localhost:6400
 *   PYTHONPATH=. python3 -m products.ce_son.main
 * 
 * Run: npx playwright test tests/e2e/ce-son.spec.js
 */
const { test, expect } = require('@playwright/test');

const BASE = 'http://localhost:6400';

test.describe('Ce-Son API Health', () => {
  test('API health endpoint returns ok', async ({ request }) => {
    const resp = await request.get(`${BASE}/api/health`);
    expect(resp.ok()).toBeTruthy();
    const data = await resp.json();
    expect(data.status).toBe('ok');
  });

  test('Register a seller', async ({ request }) => {
    const resp = await request.post(`${BASE}/api/sellers/register`, {
      data: {
        name: 'E2E Vendedor',
        phone: '5216629999001',
        email: 'e2e@test.com',
      },
    });
    expect(resp.ok()).toBeTruthy();
    const data = await resp.json();
    expect(data.ok).toBe(true);
    expect(data.seller.name).toBe('E2E Vendedor');
  });

  test('Create order and verify lifecycle', async ({ request }) => {
    // Create order
    const createResp = await request.post(`${BASE}/api/orders`, {
      data: {
        client_name: 'E2E Cliente',
        client_phone: '5216629999002',
        client_address: 'Calle E2E #456',
        items: [
          { flavor: 'uva', qty: 2, price: 250, name: 'Uva', emoji: '🍇' },
          { flavor: 'fresa', qty: 1, price: 350, name: 'Fresa', emoji: '🍓' },
        ],
        total: 850,
        payment_method: 'mercadopago',
      },
    });
    expect(createResp.ok()).toBeTruthy();
    const order = (await createResp.json()).order;
    expect(order.status).toBe('pendiente');

    // Get order
    const getResp = await request.get(`${BASE}/api/orders/${order.id}`);
    expect(getResp.ok()).toBeTruthy();
    const fetched = (await getResp.json()).order;
    expect(fetched.id).toBe(order.id);
    expect(fetched.items.length).toBe(2);

    // Update status
    const updateResp = await request.post(
      `${BASE}/api/orders/${order.id}/status?status=entregado&actor=e2e`
    );
    expect(updateResp.ok()).toBeTruthy();
    const updated = (await updateResp.json()).order;
    expect(updated.status).toBe('entregado');
  });

  test('Seller dashboard returns metrics', async ({ request }) => {
    // Register seller
    const regResp = await request.post(`${BASE}/api/sellers/register`, {
      data: { name: 'Dashboard E2E', phone: '5216629999003' },
    });
    const sid = (await regResp.json()).seller.id;

    const dashResp = await request.get(`${BASE}/api/sellers/${sid}/dashboard`);
    expect(dashResp.ok()).toBeTruthy();
    const dash = await dashResp.json();
    expect(dash).toHaveProperty('seller');
    expect(dash).toHaveProperty('total_orders');
  });

  test('Owner report aggregates data', async ({ request }) => {
    const resp = await request.get(`${BASE}/api/owner/report`);
    expect(resp.ok()).toBeTruthy();
    const report = await resp.json();
    expect(report).toHaveProperty('total_orders');
    expect(report).toHaveProperty('total_sellers');
    expect(report).toHaveProperty('total_revenue');
    expect(typeof report.total_revenue).toBe('number');
  });
});

test.describe('Ce-Son Frontend', () => {
  test('Frontend loads and shows login', async ({ page }) => {
    await page.goto(`${BASE}/frontends/ce-son/index.html`);
    // Should show login screen
    await expect(page.locator('#login-screen')).toBeVisible();
    await expect(page.locator('text=Ce-Son Vendedores')).toBeVisible();
  });
});
