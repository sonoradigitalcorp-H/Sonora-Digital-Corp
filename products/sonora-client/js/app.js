// ─── Client App ───
const API = 'http://localhost:5100';
let WS = null;
let AUTH_TOKEN = localStorage.getItem('sonora_token') || '';
let TENANT_ID = localStorage.getItem('sonora_tenant') || '';

// ─── Supabase ───
const SUPABASE_URL = 'https://your-project.supabase.co';
const SUPABASE_ANON_KEY = '';

// ─── Auth ───
function loginGoogle() {
  const redirect = encodeURIComponent(`${window.location.origin}/auth/callback`);
  window.location.href = `${SUPABASE_URL}/auth/v1/authorize?provider=google&redirect_to=${redirect}`;
}

async function loginEmail() {
  const email = document.getElementById('login-email').value;
  const pass = document.getElementById('login-pass').value;
  if (!email || !pass) return showError('login-error', 'Ingresa email y contraseña');
  try {
    const r = await fetch(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
      method: 'POST',
      headers: {'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
      body: JSON.stringify({email, password: pass})
    });
    const d = await r.json();
    if (d.access_token) {
      AUTH_TOKEN = d.access_token;
      localStorage.setItem('sonora_token', AUTH_TOKEN);
      await verifyAndEnter(d.user);
    } else {
      showError('login-error', d.error_description || 'Error al iniciar sesión');
    }
  } catch(e) {
    // Fallback: mock login for dev
    AUTH_TOKEN = 'mock_token';
    localStorage.setItem('sonora_token', AUTH_TOKEN);
    localStorage.setItem('sonora_tenant', 'abe-music');
    enterApp({email, user_metadata: {full_name: email.split('@')[0]}});
  }
}

async function registerEmail() {
  const name = document.getElementById('reg-name').value;
  const email = document.getElementById('reg-email').value;
  const pass = document.getElementById('reg-pass').value;
  if (!name || !email || !pass) return showError('register-error', 'Completa todos los campos');
  try {
    const r = await fetch(`${SUPABASE_URL}/auth/v1/signup`, {
      method: 'POST',
      headers: {'apikey': SUPABASE_ANON_KEY, 'Content-Type': 'application/json'},
      body: JSON.stringify({email, password: pass, data: {full_name: name}})
    });
    const d = await r.json();
    if (d.id) {
      toast('Cuenta creada. Revisa tu correo para verificar.');
      showLogin();
    } else {
      showError('register-error', d.msg || 'Error al registrarse');
    }
  } catch(e) {
    toast('Error de conexión', 'error');
  }
}

async function verifyAndEnter(user) {
  const tenant = user?.user_metadata?.tenant_id || 'abe-music';
  localStorage.setItem('sonora_tenant', tenant);
  enterApp(user);
}

function enterApp(user) {
  document.getElementById('user-email').textContent = user?.email || 'Usuario';
  document.getElementById('view-login').style.display = 'none';
  document.getElementById('view-register').style.display = 'none';
  document.getElementById('view-app').style.display = 'flex';
  initWS();
  loadDashboard();
  loadSettings();
}

function logout() {
  AUTH_TOKEN = '';
  localStorage.removeItem('sonora_token');
  localStorage.removeItem('sonora_tenant');
  if (WS) WS.close();
  document.getElementById('view-app').style.display = 'none';
  document.getElementById('view-login').style.display = 'flex';
}

function showRegister() {
  document.getElementById('view-login').style.display = 'none';
  document.getElementById('view-register').style.display = 'flex';
}
function showLogin() {
  document.getElementById('view-register').style.display = 'none';
  document.getElementById('view-login').style.display = 'flex';
}

function showError(id, msg) {
  document.getElementById(id).textContent = msg;
}

function toast(msg, type = 'success') {
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = `toast ${type}`;
  t.style.display = 'block';
  setTimeout(() => t.style.display = 'none', 3000);
}

// ─── Navigation ───
document.querySelectorAll('.sidebar nav a').forEach(a => {
  a.addEventListener('click', e => {
    e.preventDefault();
    document.querySelectorAll('.sidebar nav a').forEach(x => x.classList.remove('active'));
    a.classList.add('active');
    document.querySelectorAll('.page').forEach(p => p.style.display = 'none');
    document.getElementById(`page-${a.dataset.page}`).style.display = '';
    if (a.dataset.page === 'knowledge') loadRAGStatus();
  });
});

// ─── API ───
async function api(path) {
  try {
    const r = await fetch(`${API}${path}`);
    return await r.json();
  } catch(e) { return null; }
}

// ─── WebSocket ───
function initWS() {
  if (!TENANT_ID) return;
  try {
    WS = new WebSocket(`ws://localhost:5100/ws/${TENANT_ID}`);
    WS.onmessage = e => {
      try { const ev = JSON.parse(e.data);
        if (ev.event_type?.startsWith('payment') || ev.event_type?.startsWith('gamification')) loadDashboard();
      } catch(_) {}
    };
    WS.onclose = () => setTimeout(initWS, 3000);
  } catch(_) {}
}

// ─── Dashboard ───
async function loadDashboard() {
  const [rev, tok, greet, quests, lb] = await Promise.all([
    api(`/api/v1/dashboard/revenue?tenant_id=${TENANT_ID}`),
    api(`/api/v1/dashboard/tokens?tenant_id=${TENANT_ID}`),
    api(`/api/v1/dashboard/greetings?tenant_id=${TENANT_ID}`),
    api(`/api/v1/dashboard/quests?tenant_id=${TENANT_ID}`),
    api(`/api/v1/dashboard/leaderboard?tenant_id=${TENANT_ID}&metric=xp&limit=10`),
  ]);
  renderDashCards(rev, tok, greet, quests);
  renderRevenueChart(rev);
  renderLeaderboard(lb);
  renderGreetingCards(greet);
  renderGreetingTable(greet);
  initBeat3D(tok);
}

function renderDashCards(rev, tok, greet, quests) {
  document.getElementById('dash-cards').innerHTML = [
    {l:'Revenue Total', v:`$${(rev?.total_revenue||0).toLocaleString()}`, c:'up'},
    {l:'$BEAT Circulando', v:`${(tok?.circulating||0).toLocaleString()}`, c:'accent'},
    {l:'Quests Completadas', v:(quests?.total_completed||0).toLocaleString(), c:''},
    {l:'Usuarios Activos', v:(quests?.active_users||0).toLocaleString(), c:''},
  ].map(c => `<div class="card"><div class="label">${c.l}</div><div class="value">${c.v}</div></div>`).join('');
}

function renderRevenueChart(rev) {
  const days = rev?.daily_breakdown || [
    {date:'07/06',amount:340},{date:'07/07',amount:450},{date:'07/08',amount:380},
    {date:'07/09',amount:520},{date:'07/10',amount:610},{date:'07/11',amount:480},{date:'07/12',amount:390},
  ];
  const max = Math.max(...days.map(d => d.amount));
  document.getElementById('revenue-chart').innerHTML = days.map(d =>
    `<div class="bar"><div class="v">$${d.amount}</div><div class="fill" style="height:${(d.amount/max*100)}%"></div><div class="day">${d.date.slice(-2)}</div></div>`
  ).join('');
}

function renderLeaderboard(lb) {
  if (!lb || !lb.length) {
    document.getElementById('lb-table').innerHTML = '<tr><td colspan="5" style="text-align:center;color:var(--dim);padding:24px">Completa quests para aparecer aquí</td></tr>';
    return;
  }
  const tiers = ['gold','silver','bronze'];
  document.getElementById('lb-table').innerHTML = lb.map((u,i) =>
    `<tr><td><span class="rank ${i<3?tiers[i]:''}">${u.rank||i+1}</span></td><td>${u.user_id||`Fan #${i+1}`}</td><td>${(u.xp||0).toLocaleString()}</td><td>${(u.beat||0).toLocaleString()}</td><td><span class="sb green">${u.level||'bronze'}</span></td></tr>`
  ).join('');
}

function renderGreetingCards(g) {
  if (!g) return;
  document.getElementById('greeting-cards').innerHTML = [
    {l:'Total', v:g.total||0},{l:'Aprobados', v:g.approved||0, c:'green'},
    {l:'Pendientes', v:(g.pending||0)+(g.pending_approval||0), c:'yellow'},
    {l:'Rechazados', v:g.rejected||0, c:'red'},
  ].map(c => `<div class="card"><div class="label">${c.l}</div><div class="value" style="color:var(--${c.clr||'text'})">${c.v}</div></div>`).join('');
}

function renderGreetingTable(g) {
  if (!g) return;
  const statusMap = {approved:'green',pending:'yellow',rejected:'red',pending_approval:'purple',pending_payment:'yellow'};
  const items = [];
  for (let i = 0; i < (g.total||0) && i < 20; i++) {
    items.push({id:`GR-${100+i}`, artist:'Hector Rubio', msg:`Saludo #${i+1}`, status:['approved','pending','approved','rejected','pending_approval','approved','pending','approved'][i%8]});
  }
  document.getElementById('greeting-table').innerHTML = items.map(i =>
    `<tr><td>${i.id}</td><td>${i.artist}</td><td>${i.msg}</td><td><span class="sb ${statusMap[i.status]||''}">${i.status}</span></td></tr>`
  ).join('');
}

// ─── 3D Token Visualization ───
function initBeat3D(tok) {
  const container = document.getElementById('beat-3d');
  if (!container || container.children.length > 0) return;
  const w = container.clientWidth, h = 250;
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(60, w/h, .1, 100);
  camera.position.set(0, 1.5, 5);
  const renderer = new THREE.WebGLRenderer({alpha:true,antialias:true});
  renderer.setSize(w, h); renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
  container.appendChild(renderer.domElement);

  const count = 300; const pos = new Float32Array(count*3); const col = new Float32Array(count*3);
  for (let i = 0; i < count; i++) {
    const theta = Math.random()*Math.PI*2, phi = Math.acos(2*Math.random()-1), r = 1.2+Math.random()*1.5;
    pos[i*3]=r*Math.sin(phi)*Math.cos(theta); pos[i*3+1]=r*Math.cos(phi); pos[i*3+2]=r*Math.sin(phi)*Math.sin(theta);
    const c = new THREE.Color().setHSL(.67+Math.random()*.1, .8, .5+Math.random()*.3);
    col[i*3]=c.r; col[i*3+1]=c.g; col[i*3+2]=c.b;
  }
  const geo = new THREE.BufferGeometry();
  geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
  geo.setAttribute('color', new THREE.BufferAttribute(col, 3));
  const mat = new THREE.PointsMaterial({size:.06,vertexColors:true,transparent:true,opacity:.8,blending:THREE.AdditiveBlending});
  const pts = new THREE.Points(geo, mat); scene.add(pts);
  const ringG = new THREE.TorusGeometry(1.5, .015, 16, 48);
  const ringM = new THREE.MeshBasicMaterial({color:0x6366f1,transparent:true,opacity:.12});
  const ring = new THREE.Mesh(ringG, ringM); ring.rotation.x = Math.PI/3; scene.add(ring);
  let t = 0;
  function anim() { requestAnimationFrame(anim); t+=.003; pts.rotation.y=t*.3; pts.rotation.x=Math.sin(t*.1)*.1; ring.rotation.z+=.005; renderer.render(scene, camera); }
  anim();
  window.addEventListener('resize', () => { const w2=container.clientWidth; camera.aspect=w2/h; camera.updateProjectionMatrix(); renderer.setSize(w2, h); });
}

// ─── Revenue Page ───
async function loadRevenue() {
  const rev = await api(`/api/v1/dashboard/revenue?tenant_id=${TENANT_ID}`);
  document.getElementById('revenue-detail').innerHTML = `
    <p><strong>Total:</strong> $${(rev?.total_revenue||0).toLocaleString()}</p>
    <p><strong>Mensual:</strong> $${(rev?.monthly_revenue||0).toLocaleString()}</p>
    <p><strong>Transacciones:</strong> ${rev?.transaction_count||0}</p>
  `;
}

// ─── RAG ───
async function loadRAGStatus() {
  document.getElementById('rag-status').innerHTML = '<p style="color:var(--dim)">Conectando a Qdrant...</p>';
  const cols = await api(`/api/v1/rag/collections`);
  const count = cols?.filter(c => c.tenant_id === TENANT_ID)?.length || 0;
  document.getElementById('rag-status').innerHTML = `<p>${count} colección(es) activa(s) para tu tenant</p>`;
}

async function queryRAG() {
  const q = document.getElementById('rag-query').value;
  if (!q) return;
  document.getElementById('rag-results').innerHTML = '<p style="color:var(--dim)">Consultando...</p>';
  const results = await api(`/api/v1/rag/query?tenant_id=${TENANT_ID}&q=${encodeURIComponent(q)}`);
  if (!results || !results.length) {
    document.getElementById('rag-results').innerHTML = '<p style="color:var(--dim)">Sin resultados</p>';
    return;
  }
  document.getElementById('rag-results').innerHTML = results.map(r =>
    `<div style="padding:8px 0;border-bottom:1px solid var(--border);font-size:13px">
      <span style="color:var(--accent);font-size:11px">${(r.score*100).toFixed(0)}%</span>
      ${r.text}
      <span style="color:var(--dim);font-size:11px;display:block">${r.source||''}</span>
    </div>`
  ).join('');
}

// ─── Settings ───
async function loadSettings() {
  document.getElementById('settings-tenant').textContent = TENANT_ID || 'abe-music';
  document.getElementById('settings-pricing').innerHTML = `
    <p><strong>Precio saludo:</strong> 50 $BEAT / $5 USD</p>
    <p><strong>Pool $BEAT:</strong> 1,000,000</p>
    <p><strong>Plan:</strong> Ilimitado</p>
  `;
}

// ─── Page navigation links ───
document.querySelectorAll('.sidebar nav a').forEach(a => {
  if (a.dataset.page === 'revenue') a.addEventListener('click', () => setTimeout(loadRevenue, 100));
});

// ─── Auto-login check ───
(async function() {
  if (AUTH_TOKEN) {
    localStorage.setItem('sonora_tenant', 'abe-music');
    enterApp({email: localStorage.getItem('sonora_email') || 'Usuario'});
  }
})();
