import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';

const RPM_URL = 'https://models.readyplayer.me/67d5c9a8a1e8e3b7b8f9b0c1.glb';

const VISEME_MAP = {
  A: 0, E: 1, I: 2, O: 3, U: 4,
  M: 5, L: 6, F: 7, W: 8, rest: 9,
};

let scene, camera, renderer, controls, avatar;
let morphTargets = {};
let visemeQueue = [];
let isSpeaking = false;
let clock = new THREE.Clock();

const statusEl = document.getElementById('status');
const bubbleEl = document.getElementById('speech-bubble');

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

  document.getElementById('say-hello').addEventListener('click', () => speakPhrase('¡Hola! Bienvenido a ABE Music'));
  document.getElementById('say-think').addEventListener('click', () => speakPhrase('¿En qué puedo ayudarte hoy?'));
  document.getElementById('reset-cam').addEventListener('click', () => {
    camera.position.set(0, 1.5, 2.5);
    controls.target.set(0, 1.2, 0);
  });

  animate();
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
    (err) => {
      statusEl.textContent = 'Error cargando avatar';
    }
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
      else if ('aeiou'.includes(ch)) viseme = ch.toUpperCase();
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

async function speakPhrase(text) {
  if (isSpeaking) return;
  isSpeaking = true;
  bubbleEl.style.display = 'block';
  bubbleEl.textContent = text;
  document.getElementById('say-hello').disabled = true;
  document.getElementById('say-think').disabled = true;

  const visemes = generateVisemes(text);
  visemeQueue = visemes;
  let startTime = clock.getElapsedTime();

  const totalDuration = visemes.length > 0 ? visemes[visemes.length - 1].end : 1;
  await new Promise((resolve) => setTimeout(resolve, totalDuration * 1000 + 200));

  visemeQueue = [];
  resetMorphs();
  isSpeaking = false;
  bubbleEl.style.display = 'none';
  document.getElementById('say-hello').disabled = false;
  document.getElementById('say-think').disabled = false;
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
      child.morphTargetInfluences.forEach((_, i) => {
        child.morphTargetInfluences[i] = 0;
      });
      if (child.morphTargetInfluences[idx] !== undefined) {
        child.morphTargetInfluences[idx] = weight;
      }
    }
  });
}

function updateVisemes() {
  if (visemeQueue.length === 0) {
    resetMorphs();
    return;
  }

  const now = clock.getElapsedTime();
  const current = visemeQueue.find((v) => now >= v.start && now < v.end);

  if (current) {
    applyViseme(current.viseme, 1.0);
  } else if (now > visemeQueue[visemeQueue.length - 1].end) {
    visemeQueue = [];
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
