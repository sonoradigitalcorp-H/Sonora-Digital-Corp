let pc = null;
let ws = null;
let callActive = false;
let callStartTime = null;
let timerInterval = null;
let audioContext = null;

const callBtn = document.getElementById('call-btn');
const hangupBtn = document.getElementById('hangup-btn');
const statusEl = document.getElementById('connection-status');
const timerEl = document.getElementById('call-timer');
const chatLog = document.getElementById('chat-log');
const greeting = document.getElementById('greeting');

function log(msg, type = 'system') {
  const div = document.createElement('div');
  div.className = type;
  div.textContent = msg;
  chatLog.appendChild(div);
  chatLog.scrollTop = chatLog.scrollHeight;
}

function setStatus(text, cls) {
  statusEl.textContent = text;
  statusEl.className = cls || '';
}

function updateTimer() {
  if (!callStartTime) return;
  const elapsed = Math.floor((Date.now() - callStartTime) / 1000);
  const m = String(Math.floor(elapsed / 60)).padStart(2, '0');
  const s = String(elapsed % 60).padStart(2, '0');
  timerEl.textContent = `${m}:${s}`;
}

async function startCall() {
  try {
    setStatus('Conectando...', '');
    log('Iniciando llamada...', 'system');

    ws = new WebSocket(`ws://${location.host}/ws`);
    ws.onopen = async () => {
      log('WebSocket conectado', 'system');
      pc = new RTCPeerConnection({
        iceServers: [{ urls: 'stun:stun.l.google.com:19302' }]
      });

      pc.ontrack = (event) => {
        const audio = document.createElement('audio');
        audio.srcObject = event.streams[0];
        audio.autoplay = true;
        log('Recibiendo audio del servidor', 'system');
      };

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      stream.getTracks().forEach(track => pc.addTrack(track, stream));
      log('Micrófono activado', 'system');

      pc.oniceconnectionstatechange = () => {
        if (pc.iceConnectionState === 'disconnected') {
          endCall();
        }
      };

      pc.onicecandidate = (e) => {
        if (e.candidate) {
          ws.send(JSON.stringify({ type: 'candidate', candidate: e.candidate }));
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
      ws.send(JSON.stringify({ type: 'offer', sdp: offer.sdp }));
      log('Oferta WebRTC enviada', 'system');
    };

    ws.onmessage = async (event) => {
      const msg = JSON.parse(event.data);
      switch (msg.type) {
        case 'answer':
          await pc.setRemoteDescription(new RTCSessionDescription({ type: 'answer', sdp: msg.sdp }));
          setStatus('Conectado', 'connected');
          callActive = true;
          callStartTime = Date.now();
          timerInterval = setInterval(updateTimer, 1000);
          callBtn.disabled = true;
          hangupBtn.disabled = false;
          greeting.textContent = 'En llamada';
          log('Llamada establecida', 'system');
          break;
        case 'candidate':
          if (pc.remoteDescription) {
            await pc.addIceCandidate(new RTCIceCandidate(msg.candidate));
          }
          break;
        case 'transcript':
          log(`Tú: ${msg.text}`, 'user');
          break;
        case 'response':
          log(`Mystica: ${msg.text}`, 'bot');
          break;
        case 'error':
          log(`Error: ${msg.text}`, 'system');
          break;
        case 'close':
          log('Llamada finalizada por el servidor', 'system');
          endCall();
          break;
      }
    };

    ws.onclose = () => {
      log('WebSocket cerrado', 'system');
      endCall();
    };

    ws.onerror = (err) => {
      log(`Error de WebSocket`, 'system');
      console.error(err);
    };

  } catch (err) {
    log(`Error: ${err.message}`, 'system');
    console.error(err);
  }
}

function endCall() {
  if (pc) {
    pc.close();
    pc = null;
  }
  if (ws) {
    ws.close();
    ws = null;
  }
  if (timerInterval) {
    clearInterval(timerInterval);
    timerInterval = null;
  }
  callActive = false;
  callStartTime = null;
  callBtn.disabled = false;
  hangupBtn.disabled = true;
  setStatus('Desconectado', 'disconnected');
  greeting.textContent = 'Mystica';
  timerEl.textContent = '00:00';
}

callBtn.addEventListener('click', startCall);
hangupBtn.addEventListener('click', endCall);
