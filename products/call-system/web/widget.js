(function() {
  'use strict';

  // Config
  const SERVER = window.MYSTICA_SERVER || (location.protocol === 'https:' ? 'wss://' : 'ws://') + location.host;
  const COLORS = window.MYSTICA_COLORS || { primary: '#AC6D3E', secondary: '#CD8D5D', glow: 'rgba(172,109,62,0.3)' };

  // Inject styles
  const style = document.createElement('style');
  style.textContent = `
@keyframes mpulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.7;transform:scale(1.05)}}
@keyframes mspin{from{transform:rotate(0deg)}to{transform:rotate(360deg)}}
@keyframes mfade{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:translateY(0)}}
.mw-container{position:fixed;bottom:24px;right:24px;z-index:2147483647;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}
.mw-orbe{width:64px;height:64px;border-radius:50%;background:linear-gradient(135deg,${COLORS.primary},${COLORS.secondary});box-shadow:0 4px 24px ${COLORS.glow};cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:28px;transition:all .3s;animation:mpulse 3s ease-in-out infinite;position:relative;border:none;color:#000}
.mw-orbe:hover{transform:scale(1.1);box-shadow:0 8px 40px ${COLORS.glow}}
.mw-orbe .ring{position:absolute;inset:-4px;border-radius:50%;border:2px solid ${COLORS.primary};opacity:.3;animation:mspin 8s linear infinite}
.mw-orbe .ring2{position:absolute;inset:-8px;border-radius:50%;border:1px solid ${COLORS.secondary};opacity:.15;animation:mspin 12s linear infinite reverse}
.mw-panel{display:none;position:fixed;bottom:100px;right:24px;width:360px;height:500px;background:rgba(10,14,23,0.96);backdrop-filter:blur(24px);border:1px solid rgba(172,109,62,0.15);border-radius:16px;box-shadow:0 16px 64px rgba(0,0,0,0.6);flex-direction:column;overflow:hidden;animation:mfade .3s ease}
.mw-panel.open{display:flex}
.mw-header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;border-bottom:1px solid rgba(255,255,255,0.06);background:rgba(0,0,0,0.2)}
.mw-header .name{display:flex;align-items:center;gap:8px;font-size:13px;font-weight:600;color:#e8edf5}
.mw-header .name .dot{width:6px;height:6px;border-radius:50%;background:#10b981;animation:mpulse 2s infinite;display:inline-block}
.mw-header .close{width:28px;height:28px;border-radius:50%;border:none;background:rgba(255,255,255,0.05);color:#888;font-size:14px;cursor:pointer;display:flex;align-items:center;justify-content:center;transition:.2s}
.mw-header .close:hover{background:rgba(239,68,68,0.2);color:#ef4444}
.mw-chat{flex:1;overflow-y:auto;padding:12px;display:flex;flex-direction:column;gap:8px}
.mw-chat:empty::after{content:'Toca el orbe para hablar...';display:block;text-align:center;color:rgba(232,237,245,0.3);padding:60px 20px;font-size:13px;font-weight:300}
.mw-msg{display:flex;gap:6px;max-width:90%;animation:mfade .25s ease}
.mw-msg.user{flex-direction:row-reverse;margin-left:auto}
.mw-msg.bot{margin-right:auto}
.mw-msg .av{width:24px;height:24px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:9px;flex-shrink:0;margin-top:2px}
.mw-msg.user .av{background:${COLORS.primary};color:#000;order:1}
.mw-msg.bot .av{background:${COLORS.secondary};color:#000;font-weight:700}
.mw-msg .bubble{padding:8px 12px;border-radius:10px;font-size:12px;line-height:1.5;word-wrap:break-word}
.mw-msg.user .bubble{background:${COLORS.primary};color:#000;border-bottom-right-radius:2px}
.mw-msg.bot .bubble{background:rgba(255,255,255,0.04);border:1px solid rgba(172,109,62,0.1);border-bottom-left-radius:2px;color:#e8edf5}
.mw-input{display:flex;gap:6px;padding:8px 12px;border-top:1px solid rgba(255,255,255,0.06)}
.mw-input input{flex:1;background:rgba(255,255,255,0.03);border:1px solid rgba(255,255,255,0.08);border-radius:8px;padding:8px 12px;color:#e8edf5;font-size:12px;outline:none;font-family:inherit}
.mw-input input::placeholder{color:rgba(232,237,245,0.25)}
.mw-input button{width:32px;height:32px;border-radius:50%;border:none;background:${COLORS.primary};color:#000;font-size:13px;cursor:pointer;transition:.2s;display:flex;align-items:center;justify-content:center}
.mw-input button:hover{background:${COLORS.secondary};transform:scale(1.05)}
.mw-powered{text-align:center;padding:4px;font-size:8px;color:rgba(255,255,255,0.12)}
.mw-powered a{color:${COLORS.primary};text-decoration:none}
  `;
  document.head.appendChild(style);

  // HTML
  const container = document.createElement('div');
  container.className = 'mw-container';
  container.innerHTML = `
    <button class="mw-orbe" id="mwOrbe">
      <div class="ring"></div><div class="ring2"></div>
      <span>✦</span>
    </button>
    <div class="mw-panel" id="mwPanel">
      <div class="mw-header">
        <div class="name"><span class="dot"></span> Mystica</div>
        <button class="close" id="mwClose">✕</button>
      </div>
      <div class="mw-chat" id="mwChat"></div>
      <div class="mw-input">
        <input id="mwInput" placeholder="Escribe un mensaje..." />
        <button id="mwSend">➤</button>
      </div>
      <div class="mw-powered">✦ <a href="https://sonoradigitalcorp.com" target="_blank">Sonora Digital Corp</a></div>
    </div>
  `;
  document.body.appendChild(container);

  // State
  let ws = null, pc = null, isOpen = false, callActive = false;
  const chat = document.getElementById('mwChat');
  const panel = document.getElementById('mwPanel');
  const input = document.getElementById('mwInput');

  function addMsg(text, type) {
    const d = document.createElement('div'); d.className = 'mw-msg ' + type;
    const av = document.createElement('div'); av.className = 'av'; av.textContent = type === 'user' ? 'Tú' : 'M';
    const bb = document.createElement('div'); bb.className = 'bubble'; bb.textContent = text;
    if (type === 'user') { d.appendChild(bb); d.appendChild(av) } else { d.appendChild(av); d.appendChild(bb) }
    chat.appendChild(d); chat.scrollTop = chat.scrollHeight;
  }

  async function startCall() {
    if (callActive) return;
    addMsg('Conectando...', 'bot');
    try {
      const wsProto = location.protocol === 'https:' ? 'wss:' : 'ws:';
      ws = new WebSocket(`${wsProto}//${location.host}/ws`);
      ws.onopen = async () => {
        pc = new RTCPeerConnection({ iceServers: [{ urls: 'stun:stun.l.google.com:19302' }] });
        pc.ontrack = e => { const a = document.createElement('audio'); a.srcObject = e.streams[0]; a.autoplay = true };
        const s = await navigator.mediaDevices.getUserMedia({ audio: true });
        s.getTracks().forEach(t => pc.addTrack(t, s));
        pc.onicecandidate = e => { if (e.candidate) ws.send(JSON.stringify({ type: 'candidate', candidate: e.candidate })) };
        const o = await pc.createOffer(); await pc.setLocalDescription(o);
        ws.send(JSON.stringify({ type: 'offer', sdp: o.sdp }));
      };
      ws.onmessage = e => {
        const m = JSON.parse(e.data);
        if (m.type === 'answer') {
          pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: m.sdp }));
          callActive = true;
          addMsg('✅ Llamada establecida. Habla cuando quieras.', 'bot');
        }
        if (m.type === 'candidate' && pc?.remoteDescription) pc.addIceCandidate(new RTCIceCandidate(m.candidate)).catch(() => {});
        if (m.type === 'transcript') addMsg(m.text, 'user');
        if (m.type === 'response') addMsg(m.text, 'bot');
        if (m.type === 'close') { addMsg('Llamada finalizada', 'bot'); endCall(); }
      };
      ws.onclose = () => { if (callActive) addMsg('Conexión cerrada', 'bot'); callActive = false; };
      ws.onerror = () => addMsg('Error de conexión', 'bot');
    } catch (e) { addMsg('Error: ' + e.message, 'bot'); }
  }

  function endCall() {
    if (pc) { pc.close(); pc = null }
    if (ws) { ws.close(); ws = null }
    callActive = false;
  }

  function sendText() {
    const t = input.value.trim();
    if (!t || !ws) return;
    addMsg(t, 'user');
    ws.send(JSON.stringify({ type: 'text', text: t }));
    input.value = '';
  }

  // Events
  document.getElementById('mwOrbe').onclick = () => {
    isOpen = !isOpen;
    panel.classList.toggle('open', isOpen);
    if (isOpen && !callActive) startCall();
  };
  document.getElementById('mwClose').onclick = () => { panel.classList.remove('open'); isOpen = false; };
  document.getElementById('mwSend').onclick = sendText;
  input.onkeydown = e => { if (e.key === 'Enter') sendText(); };
})();
