import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const RPM_URL = 'https://models.readyplayer.me/67d5c9a8a1e8e3b7b8f9b0c1.glb';
const WS_URL = `ws://${location.host}/ws`;

const VISEME_MAP = { A: 0, E: 1, I: 2, O: 3, U: 4, M: 5, L: 6, F: 7, W: 8, rest: 9 };

let scene, camera, renderer, controls, avatar;
let morphTargets = {};
let visemeQueue = [];
let isSpeaking = false;
let clock = new THREE.Clock();
let ws = null;
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let currentAudio = null;
let sessionId = null;
let heartbeatInterval = null;

const statusEl = document.getElementById('status');
const bubbleEl = document.getElementById('speech-bubble');
const micBtn = document.getElementById('mic-btn');
const wsDot = document.getElementById('ws-dot');

function init() {
  scene = new THREE.Scene();
  scene.background = new THREE.Color(0x0a0a12);

  camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 100);
  camera.position.set(0, 1.5, 2.5);

  renderer = new THREE.WebGLRenderer({ antialias: true });
  renderer.setSize(window.innerWidth, window.innerHeight);
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  document.getElementById('canvas-container').appendChild(renderer.domElement);

  controls = new OrbitControls(camera, renderer.domElement);
  controls.target.set(0, 1.2, 0);
  controls.enableDamping = true;
  controls.update();

  const hemi = new THREE.HemisphereLight(0xffffff, 0x444444, 1);
  scene.add(hemi);
  const key = new THREE.DirectionalLight(0xffffff, 2);
  key.position.set(1, 2, 2);
  scene.add(key);
  const fill = new THREE.DirectionalLight(0xFFD700, 0.5);
  fill.position.set(-1, 1, 1);
  scene.add(fill);

  window.addEventListener('resize', onResize);
  loadAvatar();
  connectWS();

  document.getElementById('reset-cam').addEventListener('click', () => {
    camera.position.set(0, 1.5, 2.5);
    controls.target.set(0, 1.2, 0);
  });

  micBtn.addEventListener('click', toggleRecording);

  animate();
}

function connectWS() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => {
    wsDot.className = 'connected';
    statusEl.textContent = 'Conectado';
    heartbeatInterval = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send(JSON.stringify({ type: 'ping' }));
    }, 30000);
  };
  ws.onclose = () => {
    wsDot.className = 'disconnected';
    statusEl.textContent = 'Desconectado. Reconectando...';
    clearInterval(heartbeatInterval);
    setTimeout(connectWS, 3000);
  };
  ws.onmessage = (ev) => {
    const msg = JSON.parse(ev.data);
    handleMessage(msg);
  };
}

function handleMessage(msg) {
  if (msg.type === 'pong') return;
  if (msg.type === 'auth_ok') return;
  if (msg.type === 'error') {
    statusEl.textContent = 'Error: ' + msg.error;
    return;
  }

  if (msg.type === 'chat_response') {
    const text = msg.text || '';
    bubbleEl.style.display = 'block';
    bubbleEl.textContent = text;
    speakText(text);
    return;
  }

  if (msg.type === 'audio_response') {
    sessionId = msg.session_id || sessionId;
    if (msg.final) {
      const transcript = msg.text || '';
      const response = msg.response || '';
      bubbleEl.style.display = 'block';
      bubbleEl.textContent = transcript + '\n\n' + response;

      if (msg.audio) {
        const audioBytes = Uint8Array.from(atob(msg.audio), c => c.charCodeAt(0));
        const blob = new Blob([audioBytes], { type: 'audio/wav' });
        const url = URL.createObjectURL(blob);
        const audio = new Audio(url);
        currentAudio = audio;
        audio.onended = () => {
          isSpeaking = false;
          resetMorphs();
          bubbleEl.style.display = 'none';
          URL.revokeObjectURL(url);
        };
        const visemes = generateVisemes(response);
        visemeQueue = visemes;
        isSpeaking = true;
        audio.play();
        statusEl.textContent = 'Hablando...';
      }
    }
    return;
  }
}

async function toggleRecording() {
  if (isRecording) {
    stopRecording();
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
    audioChunks = [];
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) audioChunks.push(e.data);
    };
    mediaRecorder.onstop = async () => {
      stream.getTracks().forEach(t => t.stop());
      const blob = new Blob(audioChunks, { type: 'audio/webm' });
      const reader = new FileReader();
      reader.onloadend = () => {
        const b64 = reader.result.split(',')[1];
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            type: 'audio_chunk',
            audio: b64,
            session_id: sessionId,
            final: true,
          }));
        }
      };
      reader.readAsDataURL(blob);
      micBtn.className = 'mic-off';
      isRecording = false;
      statusEl.textContent = 'Procesando...';
    };
    mediaRecorder.start();
    isRecording = true;
    micBtn.className = 'mic-recording';
    statusEl.textContent = 'Escuchando...';
  } catch (err) {
    statusEl.textContent = 'Error: micrófono no disponible';
  }
}

function stopRecording() {
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop();
  }
}

function loadAvatar() {
  const loader = new GLTFLoader();
  loader.load(
    RPM_URL,
    (gltf) => {
      avatar = gltf.scene;
      avatar.scale.set(1, 1, 1);
      avatar.position.y = 0;
      scene.add(avatar);
      statusEl.textContent = 'Avatar listo';
      extractMorphTargets(avatar);
    },
    (xhr) => {
      const pct = Math.round((xhr.loaded / xhr.total) * 100);
      statusEl.textContent = `Cargando avatar... ${pct}%`;
    },
    () => { statusEl.textContent = 'Error cargando avatar'; }
  );
}

function extractMorphTargets(obj) {
  obj.traverse((child) => {
    if (child.isSkinnedMesh && child.morphTargetDictionary) {
      morphTargets = child.morphTargetDictionary;
    }
  });
}

function generateVisemes(text) {
  const words = text.split(/\s+/);
  const visemes = [];
  const durationPerWord = 0.3;
  words.forEach((word, i) => {
    const chars = word.toLowerCase().split('');
    chars.forEach((ch, j) => {
      let viseme = 'rest';
      if ('aeiou'.includes(ch)) viseme = ch.toUpperCase();
      else if ('bmp'.includes(ch)) viseme = 'M';
      else if ('fv'.includes(ch)) viseme = 'F';
      else if ('l'.includes(ch)) viseme = 'L';
      else if ('w'.includes(ch)) viseme = 'W';
      const t = (i * durationPerWord) + (j / chars.length) * durationPerWord;
      visemes.push({ viseme, start: t, end: t + durationPerWord / chars.length });
    });
  });
  if (visemes.length > 0) {
    const last = visemes[visemes.length - 1];
    visemes.push({ viseme: 'rest', start: last.end, end: last.end + 0.3 });
  }
  return visemes;
}

function speakText(text) {
  if (!text) return;
  const visemes = generateVisemes(text);
  visemeQueue = visemes;
  isSpeaking = true;
  statusEl.textContent = 'Hablando...';
}

function resetMorphs() {
  if (!avatar) return;
  avatar.traverse((child) => {
    if (child.isSkinnedMesh && child.morphTargetInfluences) {
      for (let i = 0; i < child.morphTargetInfluences.length; i++) {
        child.morphTargetInfluences[i] = 0;
      }
    }
  });
}

function applyViseme(visemeName, weight) {
  if (!avatar || !morphTargets) return;
  const idx = morphTargets[visemeName];
  if (idx === undefined) return;
  avatar.traverse((child) => {
    if (child.isSkinnedMesh && child.morphTargetInfluences) {
      child.morphTargetInfluences.forEach((_, i) => { child.morphTargetInfluences[i] = 0; });
      if (child.morphTargetInfluences[idx] !== undefined) {
        child.morphTargetInfluences[idx] = weight;
      }
    }
  });
}

function updateVisemes() {
  if (visemeQueue.length === 0) {
    if (isSpeaking && !currentAudio) {
      isSpeaking = false;
      bubbleEl.style.display = 'none';
      statusEl.textContent = 'Avatar listo';
    }
    resetMorphs();
    return;
  }
  const now = clock.getElapsedTime();
  const current = visemeQueue.find(v => now >= v.start && now < v.end);
  if (current) {
    applyViseme(current.viseme, 1.0);
  } else if (now > visemeQueue[visemeQueue.length - 1].end) {
    visemeQueue = [];
    if (!currentAudio) {
      isSpeaking = false;
      bubbleEl.style.display = 'none';
      statusEl.textContent = 'Avatar listo';
    }
    resetMorphs();
  }
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  updateVisemes();
  renderer.render(scene, camera);
}

function onResize() {
  camera.aspect = window.innerWidth / window.innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(window.innerWidth, window.innerHeight);
}

init();
