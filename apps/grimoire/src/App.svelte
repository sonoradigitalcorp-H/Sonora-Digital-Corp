<script>
  import { onMount, onDestroy } from "svelte";
  import * as THREE from "three";

  let canvasContainer;
  let scene, camera, renderer;
  let infinityGroup, particleSystem;
  let serviceNodes = [];
  let clock = 0;
  let ws;
  let animationId;

  // Reactive state
  let status = "conectando";
  let statusClass = "offline";
  let activeSessions = 0;
  let dailyCost = 0;
  let memoryCount = 47;
  let voiceActive = false;
  let wakeActive = false;
  let notifications = [];
  let gasLevel = 0;
  let systemUptime = "0s";
  let containersOnline = 0;
  let currentTime = "";
  let loading = true;

  const COLORS = {
    gold: 0xC8924B, goldLight: 0xE0AD6E, sage: 0xa8b589,
    cyan: 0x00d4ff, purple: 0x7b2fff, pink: 0xff006e, ember: 0xc0603a,
  };

  const SERVICES = [
    { id:"voice", name:"Voice", color:COLORS.cyan, port:8900 },
    { id:"kokoro", name:"Kokoro TTS", color:COLORS.sage },
    { id:"brain", name:"Brain", color:COLORS.purple, port:8100 },
    { id:"hermes", name:"Hermes", color:COLORS.gold, port:18789 },
    { id:"shield", name:"Shield", color:COLORS.cyan },
    { id:"engram", name:"Engram", color:COLORS.goldLight },
    { id:"gitea", name:"Gitea", color:COLORS.ember, port:3080 },
    { id:"ollama", name:"Ollama", color:COLORS.purple, port:11434 },
  ];

  onMount(() => {
    initScene();
    connectWS();
    fetchSystemData();
    startClock();
    setTimeout(() => loading = false, 800);
  });

  onDestroy(() => {
    if (animationId) cancelAnimationFrame(animationId);
    if (ws) ws.close();
    if (renderer) {
      renderer.dispose();
      if (renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement);
    }
  });

  function initScene() {
    scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x08090f, 0.0015);

    camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 2000);
    camera.position.set(0, 0, 18);

    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x08090f, 0);
    canvasContainer.appendChild(renderer.domElement);

    scene.add(new THREE.AmbientLight(0x222244, 0.5));
    const dl = new THREE.DirectionalLight(0xffeedd, 0.8);
    dl.position.set(1, 1, 1);
    scene.add(dl);
    const bl = new THREE.DirectionalLight(0x4444ff, 0.3);
    bl.position.set(-1, -1, -1);
    scene.add(bl);

    buildInfinity();
    buildStarfield();
    buildServiceNodes();
    buildConnections();

    window.addEventListener("resize", onResize);
    document.addEventListener("mousemove", onMouseMove);
    animate();
  }

  function buildInfinity() {
    infinityGroup = new THREE.Group();
    scene.add(infinityGroup);

    const pts = [];
    const n = 300;
    for (let i = 0; i <= n; i++) {
      const t = (i / n) * Math.PI * 2;
      const s = 5.0;
      pts.push(new THREE.Vector3(
        s * Math.cos(t) / (1 + Math.sin(t) ** 2),
        s * Math.sin(t) * Math.cos(t) / (1 + Math.sin(t) ** 2),
        Math.sin(t * 2) * 0.8
      ));
    }

    const curve = new THREE.CatmullRomCurve3(pts, true);
    infinityGroup.add(new THREE.Mesh(
      new THREE.TubeGeometry(curve, 200, 0.08, 8, true),
      new THREE.MeshBasicMaterial({ color: COLORS.gold, transparent: true, opacity: 0.15, wireframe: true })
    ));
    infinityGroup.add(new THREE.Mesh(
      new THREE.TubeGeometry(curve, 100, 0.2, 16, true),
      new THREE.MeshBasicMaterial({ color: COLORS.goldLight, transparent: true, opacity: 0.04, side: THREE.DoubleSide })
    ));

    const pcount = 600;
    const pos = new Float32Array(pcount * 3);
    for (let i = 0; i < pcount; i++) {
      const t = (i / pcount) * Math.PI * 2;
      const s = 5.0;
      pos[i*3] = s * Math.cos(t) / (1 + Math.sin(t) ** 2);
      pos[i*3+1] = s * Math.sin(t) * Math.cos(t) / (1 + Math.sin(t) ** 2);
      pos[i*3+2] = Math.sin(t * 2) * 0.8 + (Math.random() - 0.5) * 0.3;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      color: COLORS.goldLight, size: 0.08, transparent: true,
      opacity: 0.6, blending: THREE.AdditiveBlending, depthWrite: false,
    });
    particleSystem = { mesh: new THREE.Points(geo, mat), positions: pos };
    infinityGroup.add(particleSystem.mesh);
  }

  function buildStarfield() {
    const count = 2000;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 30 + Math.random() * 70;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      pos[i*3] = r * Math.sin(phi) * Math.cos(theta);
      pos[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
      pos[i*3+2] = r * Math.cos(phi);
    }
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    scene.add(new THREE.Points(geo, new THREE.PointsMaterial({
      color: 0x888899, size: 0.15, transparent: true, opacity: 0.4,
      blending: THREE.AdditiveBlending, depthWrite: false,
    })));
  }

  function buildServiceNodes() {
    SERVICES.forEach((svc, i) => {
      const angle = (i / SERVICES.length) * Math.PI * 2;
      const radius = 3.5;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = Math.sin(angle * 2) * 1.2;

      const sphere = new THREE.Mesh(
        new THREE.SphereGeometry(0.25, 16, 16),
        new THREE.MeshBasicMaterial({ color: svc.color, transparent: true, opacity: 0.8 })
      );
      sphere.position.set(x, y, z);
      scene.add(sphere);

      const glow = new THREE.Mesh(
        new THREE.SphereGeometry(0.4, 16, 16),
        new THREE.MeshBasicMaterial({ color: svc.color, transparent: true, opacity: 0.15 })
      );
      glow.position.set(x, y, z);
      scene.add(glow);

      const canvas = document.createElement("canvas");
      canvas.width = 256; canvas.height = 64;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "transparent"; ctx.fillRect(0, 0, 256, 64);
      ctx.font = "bold 18px Inter, system-ui, sans-serif";
      ctx.textAlign = "center"; ctx.fillStyle = "#edf0f7";
      ctx.fillText(svc.name, 128, 30);

      const tex = new THREE.CanvasTexture(canvas);
      tex.needsUpdate = true;
      const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.8 }));
      sprite.position.set(x, y - 0.6, z);
      sprite.scale.set(1.5, 0.4, 1);
      scene.add(sprite);

      svc.mesh = sphere; svc.glow = glow;
      svc.position = { x, y, z };
      serviceNodes.push(svc);
    });
  }

  function buildConnections() {
    serviceNodes.forEach(svc => {
      const pts = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(svc.position.x, svc.position.y, svc.position.z)];
      scene.add(new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: svc.color, transparent: true, opacity: 0.1 })
      ));
    });
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(5.8, 6.0, 64),
      new THREE.MeshBasicMaterial({ color: COLORS.gold, transparent: true, opacity: 0.04, side: THREE.DoubleSide })
    );
    ring.rotation.x = Math.PI / 2;
    scene.add(ring);
  }

  function animate() {
    animationId = requestAnimationFrame(animate);
    clock += 0.005;

    if (infinityGroup) {
      infinityGroup.rotation.x = Math.sin(clock * 0.1) * 0.1;
      infinityGroup.rotation.z = Math.cos(clock * 0.08) * 0.05;
      infinityGroup.rotation.y += 0.002;
    }

    if (particleSystem?.mesh) {
      const pos = particleSystem.mesh.geometry.attributes.position.array;
      const cnt = pos.length / 3;
      for (let i = 0; i < cnt; i++) {
        const t = (i / cnt) * Math.PI * 2 + clock * 0.3;
        const s = 5.0;
        pos[i*3] = s * Math.cos(t) / (1 + Math.sin(t) ** 2);
        pos[i*3+1] = s * Math.sin(t) * Math.cos(t) / (1 + Math.sin(t) ** 2);
        pos[i*3+2] = Math.sin(t * 2) * 0.8 + Math.sin(clock + i * 0.1) * 0.15;
      }
      particleSystem.mesh.geometry.attributes.position.needsUpdate = true;
    }

    serviceNodes.forEach((svc, i) => {
      if (svc.mesh) {
        const p = 1 + Math.sin(clock * 2 + i) * 0.15;
        svc.mesh.scale.set(p, p, p);
      }
      if (svc.glow) {
        svc.glow.material.opacity = 0.1 + Math.sin(clock * 1.5 + i * 0.7) * 0.08;
      }
    });

    camera.position.x += (mouseTarget.x * 2 - camera.position.x) * 0.01;
    camera.position.y += (mouseTarget.y * 1.5 - camera.position.y) * 0.01;
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
  }

  let mouseTarget = { x: 0, y: 0 };
  function onMouseMove(e) {
    mouseTarget.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouseTarget.y = -(e.clientY / window.innerHeight) * 2 + 1;
  }

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  function connectWS() {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    try {
      ws = new WebSocket(`${proto}//${location.host}/v1/chat`);
      ws.onopen = () => {
        status = "conectado"; statusClass = "online";
        addNotif("🟢 Sistema conectado");
      };
      ws.onclose = () => {
        status = "desconectado"; statusClass = "offline";
        setTimeout(connectWS, 3000);
      };
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === "wakeword.detected") {
            addNotif(`🔮 "${msg.keyword}" detectado`);
            wakeActive = true;
            setTimeout(() => wakeActive = false, 2000);
          }
          if (msg.type === "session.created") activeSessions++;
          if (msg.type === "status") {
            if (msg.status === "browsing") addNotif("🌐 Navegando web...");
            if (msg.status === "reading") addNotif("📖 Leyendo resultados...");
          }
        } catch(e) {}
      };
    } catch(e) { setTimeout(connectWS, 3000); }
  }

  async function fetchSystemData() {
    try {
      const r = await fetch("/api/cost/daily");
      const d = await r.json();
      dailyCost = d.total || 0;
      gasLevel = Math.min((dailyCost / 0.50) * 100, 100);
    } catch(e) {}
    try {
      const r = await fetch("/api/system/status");
      const d = await r.json();
      systemUptime = `${Math.floor((d.uptime || 0) / 3600)}h`;
      containersOnline = Object.keys(d.containers || {}).length;
    } catch(e) {}
    setInterval(() => {
      dailyCost += Math.random() * 0.002;
      gasLevel = Math.min((dailyCost / 0.50) * 100, 100);
      memoryCount = 42 + Math.floor(Math.random() * 20);
    }, 8000);
  }

  function startClock() {
    setInterval(() => {
      const n = new Date();
      currentTime = n.toLocaleTimeString("es-MX", { hour:"2-digit", minute:"2-digit", second:"2-digit", hour12:false });
    }, 1000);
  }

  function addNotif(text) {
    const id = Date.now();
    notifications = [...notifications, { id, text }];
    setTimeout(() => { notifications = notifications.filter(n => n.id !== id); }, 4000);
  }

  async function toggleVoice() {
    if (voiceActive) {
      if (window.mediaRecorder && window.mediaRecorder.state !== "inactive") window.mediaRecorder.stop();
      voiceActive = false;
    } else {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          audio: { echoCancellation: true, noiseSuppression: true, sampleRate: 16000 }
        });
        const chunks = [];
        const mr = new MediaRecorder(stream, {
          mimeType: MediaRecorder.isTypeSupported('audio/webm;codecs=opus') ? 'audio/webm;codecs=opus' : 'audio/webm'
        });
        mr.ondataavailable = e => { if (e.data.size > 0) chunks.push(e.data); };
        mr.onstop = () => {
          stream.getTracks().forEach(t => t.stop());
          if (chunks.length && ws?.readyState === WebSocket.OPEN) {
            const reader = new FileReader();
            reader.onload = () => {
              ws.send(JSON.stringify({ type:"input_audio_buffer.append", audio: reader.result.split(",")[1] }));
              ws.send(JSON.stringify({ type:"input_audio_buffer.commit" }));
            };
            reader.readAsDataURL(new Blob(chunks, { type:"audio/webm" }));
          }
        };
        mr.start(100);
        window.mediaRecorder = mr;
        voiceActive = true;
        addNotif("🎤 Grabando...");
      } catch(e) { addNotif("⚠️ Error: micrófono requerido"); }
    }
  }
</script>

<div class="grimoire">
  <div bind:this={canvasContainer} class="canvas"></div>

  <!-- Loading -->
  {#if loading}
  <div class="loading">
    <div class="ring"></div>
    <p>Inicializando Grimoire</p>
  </div>
  {/if}

  <div class="hud">
    <div class="top-bar">
      <div class="brand">
        <h1>✦ <span>Mystic</span> Grimoire</h1>
        <div class="ver">AGENTIC OS · v3.0</div>
      </div>
      <div class="status-bar">
        <span class="dot {statusClass}"></span>
        <span class="label">{status}</span>
        <span class="time">{currentTime}</span>
      </div>
    </div>

    <div class="center">
      <div class="active-count">{activeSessions || 1}</div>
      <div class="active-label">Agentes Activos</div>
    </div>

    <div class="panels">
      <div class="panel">
        <div class="label">⛽ Gas LLM</div>
        <div class="value sage">${dailyCost.toFixed(4)}</div>
        <div class="sub">deepseek-v4-flash · $0.00026/chat</div>
        <div class="tank"><div class="fill" style="width: {gasLevel}%"></div></div>
      </div>
      <div class="panel">
        <div class="label">🧠 Memoria</div>
        <div class="value gold">{memoryCount}</div>
        <div class="sub">engram · 7 layers</div>
      </div>
      <div class="panel">
        <div class="label">🎙️ Voz</div>
        <div class="value cyan">{activeSessions}</div>
        <div class="sub">Kokoro TTS · {containersOnline} containers</div>
      </div>
      <div class="panel">
        <div class="label">🛡️ Shield</div>
        <div class="value" style="color:#00e676">✓</div>
        <div class="sub">Policy Engine · {systemUptime} uptime</div>
      </div>
    </div>
  </div>

  <div class="wake-indicator" class:visible={wakeActive}>
    <span class="dot"></span>
    <span>🔮 Escuchando "Hey Jarvis"</span>
  </div>

  <button class="voice-btn" class:recording={voiceActive} on:click={toggleVoice}>
    {voiceActive ? "⏹" : "🎤"}
  </button>

  <div class="notifications">
    {#each notifications as notif}
      <div class="notif">{notif.text}</div>
    {/each}
  </div>
</div>

<style>
  :global(*) { margin: 0; padding: 0; box-sizing: border-box; }
  :global(body) {
    background: #08090f; color: #edf0f7; overflow: hidden;
    font-family: 'Inter', system-ui, -apple-system, sans-serif;
    width: 100vw; height: 100vh;
  }
  .grimoire { width: 100%; height: 100%; position: relative; }
  .canvas { position: fixed; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }

  .loading {
    position: fixed; inset: 0; z-index: 999;
    background: #08090f; display: flex; flex-direction: column;
    align-items: center; justify-content: center; gap: 16px;
  }
  .ring {
    width: 48px; height: 48px; border: 2px solid rgba(200,146,75,0.1);
    border-top-color: #C8924B; border-radius: 50%; animation: spin 1s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .loading p { font-size: 12px; color: rgba(237,240,247,0.5); letter-spacing: 2px; text-transform: uppercase; }

  .hud {
    position: fixed; inset: 0; z-index: 10; pointer-events: none;
    display: flex; flex-direction: column; justify-content: space-between;
    padding: 20px 28px;
  }

  .top-bar { display: flex; align-items: center; justify-content: space-between; pointer-events: auto; }
  .brand h1 { font-size: 13px; font-weight: 400; letter-spacing: 4px; text-transform: uppercase; color: rgba(255,255,255,0.4); }
  .brand h1 span { color: #C8924B; }
  .ver { font-size: 10px; color: rgba(255,255,255,0.2); letter-spacing: 2px; margin-top: 2px; }
  .status-bar { display: flex; align-items: center; gap: 12px; }
  .dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot.online { background: #00e676; box-shadow: 0 0 12px #00e676; }
  .dot.offline { background: #ff3355; box-shadow: 0 0 12px #ff3355; }
  .label { font-size: 11px; color: rgba(237,240,247,0.5); letter-spacing: 1px; text-transform: uppercase; }
  .time { font-size: 11px; color: rgba(237,240,247,0.5); letter-spacing: 1px; font-variant-numeric: tabular-nums; }

  .center {
    position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
    text-align: center; pointer-events: none; z-index: 5;
  }
  .active-count {
    font-size: 48px; font-weight: 200;
    background: linear-gradient(135deg, #C8924B, #E0AD6E, #a8b589);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent; letter-spacing: 2px;
  }
  .active-label { font-size: 10px; color: rgba(237,240,247,0.5); letter-spacing: 3px; text-transform: uppercase; margin-top: -4px; }

  .panels { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 12px; pointer-events: auto; }
  .panel {
    background: rgba(17,19,30,0.7); backdrop-filter: blur(20px);
    border: 1px solid rgba(255,255,255,0.06); border-radius: 12px;
    padding: 14px 16px; transition: 0.3s;
  }
  .panel:hover { border-color: rgba(200,146,75,0.2); }
  .panel .label { font-size: 9px; text-transform: uppercase; letter-spacing: 2px; color: rgba(237,240,247,0.5); margin-bottom: 6px; }
  .value { font-size: 22px; font-weight: 600; letter-spacing: 1px; }
  .value.gold { color: #C8924B; }
  .value.sage { color: #a8b589; }
  .value.cyan { color: #00d4ff; }
  .sub { font-size: 10px; color: rgba(237,240,247,0.5); margin-top: 2px; }
  .tank { margin-top: 6px; height: 4px; background: rgba(255,255,255,0.06); border-radius: 2px; overflow: hidden; }
  .fill { height: 100%; border-radius: 2px; transition: width 1s ease; background: linear-gradient(90deg, #00e676, #ffab00, #ff3355); }

  .wake-indicator {
    position: fixed; bottom: 170px; right: 28px; z-index: 20;
    display: none; align-items: center; gap: 8px;
    background: rgba(17,19,30,0.8); backdrop-filter: blur(12px);
    border: 1px solid rgba(200,146,75,0.2); border-radius: 20px;
    padding: 8px 16px; font-size: 11px; color: #E0AD6E; pointer-events: none;
  }
  .wake-indicator.visible { display: flex; }
  .wake-indicator .dot { width: 6px; height: 6px; background: #C8924B; animation: pulse 1.5s infinite; }
  @keyframes pulse { 0%,100% { opacity: 0.3; } 50% { opacity: 1; } }

  .voice-btn {
    position: fixed; bottom: 100px; right: 28px; z-index: 20;
    width: 56px; height: 56px; border-radius: 50%;
    background: linear-gradient(135deg, #C8924B, #c0603a);
    border: none; color: #fff; font-size: 22px; cursor: pointer;
    box-shadow: 0 4px 24px rgba(200,146,75,0.3);
    transition: 0.3s; pointer-events: auto;
    display: flex; align-items: center; justify-content: center;
  }
  .voice-btn:hover { transform: scale(1.08); box-shadow: 0 6px 32px rgba(200,146,75,0.5); }
  .voice-btn.recording { background: linear-gradient(135deg, #ff3355, #ff0044); animation: rec 1s infinite; }
  @keyframes rec { 0%,100% { box-shadow: 0 4px 24px rgba(255,51,85,0.3); } 50% { box-shadow: 0 4px 48px rgba(255,51,85,0.5); } }

  .notifications {
    position: fixed; top: 80px; right: 28px; z-index: 15;
    display: flex; flex-direction: column; gap: 6px; pointer-events: none;
  }
  .notif {
    background: rgba(17,19,30,0.85); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 8px;
    padding: 10px 16px; font-size: 12px; color: #edf0f7;
    animation: slideIn 0.3s; max-width: 280px; pointer-events: auto;
  }
  @keyframes slideIn { from { transform: translateX(40px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

  @media(max-width: 768px) {
    .panels { grid-template-columns: 1fr 1fr; gap: 8px; }
    .hud { padding: 12px 16px; }
    .panel { padding: 10px 12px; }
    .value { font-size: 18px; }
  }
</style>
