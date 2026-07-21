const WS_URL = `ws://${location.host}/ws`;
const API_URL = '/api';

let ws = null;
let token = null;
let currentRole = 'director';
let currentView = 'chat';
let mediaRecorder = null;
let audioChunks = [];
let sessionId = null;

async function getToken(role) {
  const r = await fetch(`${API_URL}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ user_id: 'abraham' }),
  });
  const data = await r.json();
  token = data.access_token;
  return token;
}

function connectWS() {
  if (ws) ws.close();
  ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    ws.send(JSON.stringify({ type: 'auth', token }));
    document.getElementById('voice-status').className = 'status-dot online';
  };
  ws.onmessage = (e) => {
    const msg = JSON.parse(e.data);
    handleWSMessage(msg);
  };
  ws.onclose = () => {
    document.getElementById('voice-status').className = 'status-dot offline';
    setTimeout(connectWS, 3000);
  };
  ws.onerror = () => ws.close();
}

function handleWSMessage(msg) {
  switch (msg.type) {
    case 'auth_ok':
      addMessage('system', `Conectado como ${msg.role}`);
      break;
    case 'auth_error':
      addMessage('system', `Error de autenticación: ${msg.error}`);
      break;
    case 'chat_response':
      addMessage('assistant', msg.text);
      sessionId = msg.session_id;
      if (msg.audio) playAudio(msg.audio);
      break;
    case 'audio_response':
      if (msg.final) {
        addMessage('user', msg.text);
        addMessage('assistant', msg.response);
        sessionId = msg.session_id;
        if (msg.audio) playAudio(msg.audio);
      }
      break;
    case 'pong':
      break;
    case 'error':
      addMessage('system', `Error: ${msg.error}`);
      break;
  }
}

function addMessage(role, text) {
  const container = document.getElementById('chat-messages');
  const div = document.createElement('div');
  div.className = `msg ${role}`;
  div.textContent = text;
  container.appendChild(div);
  container.scrollTop = container.scrollHeight;
}

function playAudio(base64) {
  const audio = new Audio(`data:audio/wav;base64,${base64}`);
  audio.play().catch(() => {});
}

// Chat
async function sendChat(text) {
  if (!text.trim()) return;
  addMessage('user', text);
  document.getElementById('chat-input').value = '';

  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'chat', text, session_id: sessionId }));
  } else {
    const r = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
      body: JSON.stringify({ text, session_id: sessionId }),
    });
    const data = await r.json();
    addMessage('assistant', data.text);
    sessionId = data.session_id;
  }
}

// Voice
async function startRecording() {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    audioChunks = [];
    mediaRecorder.ondataavailable = (e) => audioChunks.push(e.data);
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const buffer = await blob.arrayBuffer();
      const base64 = btoa(String.fromCharCode(...new Uint8Array(buffer)));

      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'audio_chunk', audio: base64, session_id: sessionId, final: true }));
      } else {
        const r = await fetch(`${API_URL}/voice/process`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
          body: JSON.stringify({ audio: base64, session_id: sessionId, final: true }),
        });
        const data = await r.json();
        if (data.text) addMessage('user', data.text);
        if (data.response) addMessage('assistant', data.response);
        sessionId = data.session_id;
      }
    };
    mediaRecorder.start();
    document.getElementById('voice-btn').className = 'recording';
  } catch (e) {
    addMessage('system', `Error de micrófono: ${e.message}`);
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state === 'recording') {
    mediaRecorder.stop();
    document.getElementById('voice-btn').className = '';
  }
}

// API calls
async function apiGet(path) {
  const r = await fetch(`${API_URL}${path}`, {
    headers: { 'Authorization': `Bearer ${token}` },
  });
  return r.json();
}

async function apiPost(path, body = {}) {
  const r = await fetch(`${API_URL}${path}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  return r.json();
}

async function loadSyncStatus() {
  try {
    const s = await apiGet('/sync/status');
    const el = document.getElementById('sync-status');
    if (el) {
      el.textContent = s.last_sync ? `Último sync: ${new Date(s.last_sync).toLocaleString()}` : 'Sin sync previo';
    }
  } catch {}
}

async function triggerSync() {
  const btn = document.getElementById('sync-btn');
  const status = document.getElementById('sync-status');
  btn.disabled = true;
  btn.textContent = 'Sincronizando...';
  status.textContent = 'Recolectando datos de Deezer, Apple Music, Wikipedia...';
  try {
    const r = await fetch(`${API_URL}/sync`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
    });
    const result = await r.json();
    status.textContent = `Sync completado: ${result.merged} artistas actualizados (${result.timestamp ? new Date(result.timestamp).toLocaleTimeString() : 'ahora'})`;
    loadDashboard();
  } catch (e) {
    status.textContent = `Error: ${e.message}`;
  }
  btn.disabled = false;
  btn.textContent = '🔄 Refresh Data';
}

async function loadDashboard() {
  const el = document.getElementById('view-dashboard');
  const data = await apiGet('/ceo/dashboard');
  const syncStatus = await apiGet('/sync/status').catch(() => ({}));
  el.innerHTML = `
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;">
      <h2 style="margin:0;">CEO Dashboard</h2>
      <div style="display:flex;align-items:center;gap:8px;">
        <span id="sync-status" style="font-size:0.75rem;color:var(--text-dim);">${syncStatus.last_sync ? 'Último sync: ' + new Date(syncStatus.last_sync).toLocaleString() : 'Sin sync previo'}</span>
        <button id="sync-btn" onclick="triggerSync()" style="padding:6px 14px;background:var(--accent);color:#fff;border:none;border-radius:6px;cursor:pointer;font-size:0.8rem;">🔄 Refresh Data</button>
      </div>
    </div>
    <div class="kpi-grid">
      <div class="kpi-card"><div class="value">${data.total_artists}</div><div class="label">Artistas</div></div>
      <div class="kpi-card"><div class="value">${(data.total_streams / 1e6).toFixed(1)}M</div><div class="label">Streams</div></div>
      <div class="kpi-card"><div class="value">$${(data.total_revenue / 1000).toFixed(0)}K</div><div class="label">Revenue</div></div>
      <div class="kpi-card"><div class="value">${data.total_releases}</div><div class="label">Lanzamientos</div></div>
      <div class="kpi-card"><div class="value">${data.total_contracts}</div><div class="label">Contratos</div></div>
      <div class="kpi-card"><div class="value">${data.pending_contracts}</div><div class="label">Pendientes</div></div>
    </div>
    <h3 style="margin-bottom:8px;">Top Artistas</h3>
    ${(data.top_artists || []).map(a => `
      <div class="artist-card">
        <div class="name">${a.name}</div>
        <div class="meta">${(a.streams / 1e6).toFixed(1)}M streams · $${(a.revenue / 1000).toFixed(0)}K revenue</div>
      </div>
    `).join('')}
    <p style="margin-top:16px;font-size:0.8rem;color:var(--text-dim);">${data.generated_at}</p>
  `;
}

async function loadArtists() {
  const el = document.getElementById('view-artists');
  const data = await apiGet('/artists');
  el.innerHTML = `
    <h2 style="margin-bottom:16px;">Artistas</h2>
    ${(data.artists || []).map(a => `
      <div class="artist-card">
        <div class="name">${a.name || a.nombre}</div>
        <div class="meta">${a.genre || a.genero} · ${a.status} · ${(a.streams / 1e6).toFixed(1)}M streams</div>
      </div>
    `).join('')}
  `;
}

async function loadContracts() {
  const el = document.getElementById('view-contracts');
  const data = await apiGet('/contracts');
  el.innerHTML = `
    <h2 style="margin-bottom:16px;">Contratos</h2>
    ${(data.contracts || []).length === 0 ? '<p style="color:var(--text-dim);">No hay contratos aún</p>' : `
    <table class="table">
      <thead><tr><th>ID</th><th>Tipo</th><th>Artista</th><th>Status</th></tr></thead>
      <tbody>${data.contracts.map(c => `
        <tr><td>${c.id}</td><td>${c.type}</td><td>${c.artist_id}</td><td>${c.status}</td></tr>
      `).join('')}</tbody>
    </table>`}
  `;
}

async function loadRevenue() {
  const el = document.getElementById('view-revenue');
  const data = await apiGet('/revenue');
  el.innerHTML = `
    <h2 style="margin-bottom:16px;">Revenue</h2>
    <div class="kpi-grid">
      <div class="kpi-card"><div class="value">$${data.total_revenue || 0}</div><div class="label">Total</div></div>
      <div class="kpi-card"><div class="value">$${data.artist_total || 0}</div><div class="label">Artistas</div></div>
      <div class="kpi-card"><div class="value">$${data.label_total || 0}</div><div class="label">Label</div></div>
      <div class="kpi-card"><div class="value">$${data.distributor_total || 0}</div><div class="label">Distribución</div></div>
    </div>
  `;
}

async function loadFans() {
  const el = document.getElementById('view-fans');
  const data = await apiGet('/crm/fans');
  el.innerHTML = `
    <h2 style="margin-bottom:16px;">Fans</h2>
    ${(data.fans || []).length === 0 ? '<p style="color:var(--text-dim);">No hay fans registrados</p>' : `
    <table class="table">
      <thead><tr><th>Nombre</th><th>Teléfono</th><th>Status</th></tr></thead>
      <tbody>${data.fans.map(f => `
        <tr><td>${f.name || '-'}</td><td>${f.phone || '-'}</td><td>${f.status || '-'}</td></tr>
      `).join('')}</tbody>
    </table>`}
  `;
}

// Navigation
document.querySelectorAll('.nav-btn').forEach(btn => {
  btn.addEventListener('click', async () => {
    document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));
    const view = btn.dataset.view;
    currentView = view;
    document.getElementById(`view-${view}`).classList.add('active');

    switch (view) {
      case 'dashboard': loadDashboard(); break;
      case 'artists': loadArtists(); break;
      case 'contracts': loadContracts(); break;
      case 'revenue': loadRevenue(); break;
      case 'fans': loadFans(); break;
    }
  });
});

// Chat input
document.getElementById('send-btn').addEventListener('click', () => {
  sendChat(document.getElementById('chat-input').value);
});
document.getElementById('chat-input').addEventListener('keydown', (e) => {
  if (e.key === 'Enter') sendChat(e.target.value);
});

// Voice button
document.getElementById('voice-btn').addEventListener('mousedown', startRecording);
document.getElementById('voice-btn').addEventListener('mouseup', stopRecording);
document.getElementById('voice-btn').addEventListener('touchstart', (e) => { e.preventDefault(); startRecording(); });
document.getElementById('voice-btn').addEventListener('touchend', (e) => { e.preventDefault(); stopRecording(); });

// Role switch
document.getElementById('role-select').addEventListener('change', async (e) => {
  currentRole = e.target.value;
  await getToken(currentRole);
  connectWS();
  addMessage('system', `Cambiado a rol: ${currentRole}`);
});

// Init
(async () => {
  await getToken(currentRole);
  connectWS();
  addMessage('system', 'Bienvenido a ABE Music OS');
  addMessage('assistant', 'Hola, soy tu asistente de ABE Music. Puedes preguntarme sobre streams, revenue, contratos, artistas o lo que necesites.');
})();
