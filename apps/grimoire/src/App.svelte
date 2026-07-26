<script>
  import { onMount, onDestroy } from "svelte";
  import * as THREE from "three";
  import AvatarPage from "./lib/AvatarPage.svelte";
  import StickerSystem from "./lib/StickerSystem.svelte";

  let canvasContainer;
  let scene, camera, renderer, raycaster, mouse;
  let infinityGroup, particleSystem;
  let serviceNodes = [];
  let clock = 0;
  let ws;
  let animationId;
  let isDragging = false;
  let previousMouse = { x: 0, y: 0 };
  let autoRotate = true;
  let selectedService = null;
  let hoveredService = null;
  let tooltipStyle = "";
  let tooltipText = "";
  let showTooltip = false;

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
  let showAvatar = false;
  let activeTenant = "sonora-digital";
  let tenantName = "Sonora Digital Corp";
  let audioLevel = 0;

  const TENANTS = {
    "sonora-digital": { name: "Sonora Digital Corp", color: "#C8924B", bg: "rgba(200,146,75,0.03)" },
    "abe-music": { name: "ABE Music Group", color: "#FF6B35", bg: "rgba(255,107,53,0.03)" },
    "aztrotech": { name: "AztroTech", color: "#00d4ff", bg: "rgba(0,212,255,0.03)" },
    "nathy-conta": { name: "Nathy Conta", color: "#c9a84c", bg: "rgba(201,168,76,0.03)" },
    "el-joyero": { name: "El Joyero", color: "#d4a030", bg: "rgba(212,160,48,0.03)" },
    "mds-corp": { name: "MDS Corp", color: "#7c3aed", bg: "rgba(124,58,237,0.03)" },
  };

  const COLORS = {
    gold: 0xC8924B, goldLight: 0xE0AD6E, sage: 0xa8b589,
    cyan: 0x00d4ff, purple: 0x7b2fff, pink: 0xff006e, ember: 0xc0603a,
  };

  const SERVICES = [
    { id:"voice", name:"Voice", desc:"Mystic Voice en tiempo real con Kokoro TTS", color:COLORS.cyan, port:8900, status:"online" },
    { id:"kokoro", name:"Kokoro TTS", desc:"Síntesis de voz en español (em_alex)", color:COLORS.sage, status:"online" },
    { id:"brain", name:"Brain", desc:"Unified Brain: Engram + Neo4j + Qdrant", color:COLORS.purple, port:8100, status:"online" },
    { id:"hermes", name:"Hermes", desc:"Orquestador de agentes y MCP Gateway", color:COLORS.gold, port:18789, status:"online" },
    { id:"shield", name:"Shield", desc:"Policy Engine + Seguridad", color:COLORS.cyan, status:"online" },
    { id:"engram", name:"Engram", desc:"Memoria persistente de 7 capas", color:COLORS.goldLight, status:"online" },
    { id:"gitea", name:"Gitea", desc:"Git autogestionado (red privada)", color:COLORS.ember, port:3080, status:"online" },
    { id:"ollama", name:"Ollama", desc:"LLM local: llama3.2 + tinyllama", color:COLORS.purple, port:11434, status:"online" },
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

    raycaster = new THREE.Raycaster();
    mouse = new THREE.Vector2();

    scene.add(new THREE.AmbientLight(0x222244, 0.5));
    const dl = new THREE.DirectionalLight(0xffeedd, 0.8);
    dl.position.set(1, 1, 1); scene.add(dl);
    const bl = new THREE.DirectionalLight(0x4444ff, 0.3);
    bl.position.set(-1, -1, -1); scene.add(bl);

    buildInfinity();
    buildStarfield();
    buildServiceNodes();
    buildConnections();
    createParticleBursts();

    window.addEventListener("resize", onResize);
    renderer.domElement.addEventListener("mousemove", onMouseMove);
    renderer.domElement.addEventListener("mousedown", onMouseDown);
    renderer.domElement.addEventListener("mouseup", onMouseUp);
    renderer.domElement.addEventListener("click", onClick);
    renderer.domElement.addEventListener("touchstart", onTouchStart, { passive: true });
    renderer.domElement.addEventListener("touchmove", onTouchMove, { passive: true });
    renderer.domElement.addEventListener("touchend", onTouchEnd, { passive: true });
    animate();
    setInterval(() => { audioLevel = Math.random() * 0.2; }, 300);
  }

  // ── Infinity Symbol ──
  function buildInfinity() {
    infinityGroup = new THREE.Group();
    scene.add(infinityGroup);
    const pts = []; const n = 300;
    for (let i = 0; i <= n; i++) {
      const t = (i / n) * Math.PI * 2, s = 5.0;
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
      const t = (i / pcount) * Math.PI * 2, s = 5.0;
      pos[i*3] = s * Math.cos(t) / (1 + Math.sin(t) ** 2);
      pos[i*3+1] = s * Math.sin(t) * Math.cos(t) / (1 + Math.sin(t) ** 2);
      pos[i*3+2] = Math.sin(t * 2) * 0.8 + (Math.random() - 0.5) * 0.3;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    particleSystem = {
      mesh: new THREE.Points(geo, new THREE.PointsMaterial({
        color: COLORS.goldLight, size: 0.08, transparent: true,
        opacity: 0.6, blending: THREE.AdditiveBlending, depthWrite: false,
      })),
      positions: pos
    };
    infinityGroup.add(particleSystem.mesh);
  }

  // ── Starfield ──
  function buildStarfield() {
    const count = 2000;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 30 + Math.random() * 70, theta = Math.random() * Math.PI * 2;
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

  // ── Service Nodes with interactivity ──
  function buildServiceNodes() {
    SERVICE_SPRITES = [];
    SERVICES.forEach((svc, i) => {
      const angle = (i / SERVICES.length) * Math.PI * 2;
      const radius = 3.5;
      const x = Math.cos(angle) * radius;
      const z = Math.sin(angle) * radius;
      const y = Math.sin(angle * 2) * 1.2;

      const sphere = new THREE.Mesh(
        new THREE.SphereGeometry(0.3, 20, 20),
        new THREE.MeshBasicMaterial({ color: svc.color, transparent: true, opacity: 0.9 })
      );
      sphere.position.set(x, y, z);
      sphere.userData = { serviceId: svc.id, isNode: true };
      scene.add(sphere);

      const glow = new THREE.Mesh(
        new THREE.SphereGeometry(0.5, 16, 16),
        new THREE.MeshBasicMaterial({ color: svc.color, transparent: true, opacity: 0.12 })
      );
      glow.position.set(x, y, z);
      scene.add(glow);

      // Outer ring for selected state
      const ring = new THREE.Mesh(
        new THREE.RingGeometry(0.35, 0.45, 32),
        new THREE.MeshBasicMaterial({ color: svc.color, transparent: true, opacity: 0, side: THREE.DoubleSide })
      );
      ring.position.set(x, y, z);
      ring.lookAt(camera.position);
      scene.add(ring);

      // Label
      const canvas = document.createElement("canvas");
      canvas.width = 300; canvas.height = 72;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "transparent"; ctx.fillRect(0, 0, 300, 72);
      ctx.font = "bold 20px Inter, system-ui, sans-serif";
      ctx.textAlign = "center"; ctx.fillStyle = "#edf0f7";
      ctx.fillText(svc.name, 150, 30);
      ctx.font = "13px Inter";
      ctx.fillStyle = "rgba(237,240,247,0.4)";
      ctx.fillText("● " + svc.status.toUpperCase(), 150, 55);

      const tex = new THREE.CanvasTexture(canvas); tex.needsUpdate = true;
      const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, transparent: true, opacity: 0.9 }));
      sprite.position.set(x, y - 0.7, z);
      sprite.scale.set(1.8, 0.45, 1);
      scene.add(sprite);

      svc.mesh = sphere; svc.glow = glow; svc.ring = ring; svc.sprite = sprite;
      svc.position = { x, y, z };
      svc.origColor = svc.color;
      serviceNodes.push(svc);
    });
  }
  let SERVICE_SPRITES = [];

  // ── Connection Lines ──
  function buildConnections() {
    serviceNodes.forEach(svc => {
      const pts = [new THREE.Vector3(0, 0, 0), new THREE.Vector3(svc.position.x, svc.position.y, svc.position.z)];
      const line = new THREE.Line(
        new THREE.BufferGeometry().setFromPoints(pts),
        new THREE.LineBasicMaterial({ color: svc.color, transparent: true, opacity: 0.08 })
      );
      svc.line = line;
      scene.add(line);
    });
    const ring = new THREE.Mesh(
      new THREE.RingGeometry(5.8, 6.0, 64),
      new THREE.MeshBasicMaterial({ color: COLORS.gold, transparent: true, opacity: 0.03, side: THREE.DoubleSide })
    );
    ring.rotation.x = Math.PI / 2; scene.add(ring);
  }

  // ── Particle Burst Effect ──
  let burstParticles = [];

  function createParticleBursts() {
    const count = 100;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const vel = new Float32Array(count * 3);
    const life = new Float32Array(count);
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      color: COLORS.gold, size: 0.06, transparent: true,
      opacity: 0, blending: THREE.AdditiveBlending, depthWrite: false,
    });
    const mesh = new THREE.Points(geo, mat);
    mesh.visible = false;
    scene.add(mesh);
    burstParticles = { mesh, pos, vel, life, active: false, time: 0 };
  }

  function triggerBurst(x, y, z, color = COLORS.gold) {
    const bp = burstParticles;
    bp.active = true; bp.time = 0;
    bp.mesh.visible = true;
    bp.mesh.material.color.setHex(color);
    for (let i = 0; i < 100; i++) {
      bp.pos[i*3] = x; bp.pos[i*3+1] = y; bp.pos[i*3+2] = z;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      const speed = 0.02 + Math.random() * 0.04;
      bp.vel[i*3] = Math.sin(phi) * Math.cos(theta) * speed;
      bp.vel[i*3+1] = Math.sin(phi) * Math.sin(theta) * speed;
      bp.vel[i*3+2] = Math.cos(phi) * speed;
      bp.life[i] = 1.0 + Math.random() * 0.5;
    }
    bp.mesh.geometry.attributes.position.needsUpdate = true;
    setTimeout(() => { bp.active = false; bp.mesh.visible = false; }, 2000);
  }

  // ── Animation Loop ──
  function animate() {
    animationId = requestAnimationFrame(animate);
    clock += 0.005;

    // Auto-rotate infinity
    if (infinityGroup && autoRotate) {
      infinityGroup.rotation.x = Math.sin(clock * 0.1) * 0.1;
      infinityGroup.rotation.z = Math.cos(clock * 0.08) * 0.05;
      infinityGroup.rotation.y += 0.003;
    }

    // Animate infinity particles
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

    // Animate service nodes
    serviceNodes.forEach((svc, i) => {
      if (svc.mesh) {
        const p = 1 + Math.sin(clock * 2 + i) * 0.15;
        svc.mesh.scale.set(p, p, p);
        svc.glow.material.opacity = 0.1 + Math.sin(clock * 1.5 + i * 0.7) * 0.08;
        
        // Selected node glows brighter
        if (selectedService === svc.id) {
          svc.glow.material.opacity = 0.3 + Math.sin(clock * 3) * 0.1;
          svc.ring.material.opacity = 0.6;
          svc.ring.scale.setScalar(1 + Math.sin(clock * 2) * 0.1);
          svc.ring.lookAt(camera.position);
        } else {
          svc.ring.material.opacity = svc.id === hoveredService ? 0.3 : 0;
        }
        
        // Hover effect
        if (svc.id === hoveredService && selectedService !== svc.id) {
          svc.mesh.material.color.setHex(0xffffff);
          svc.mesh.scale.setScalar(1.4);
        } else if (selectedService !== svc.id) {
          svc.mesh.material.color.setHex(svc.origColor);
        }
      }
    });

    // Burst particles
    if (burstParticles.active) {
      const bp = burstParticles;
      bp.time += 0.016;
      for (let i = 0; i < 100; i++) {
        bp.pos[i*3] += bp.vel[i*3];
        bp.pos[i*3+1] += bp.vel[i*3+1];
        bp.pos[i*3+2] += bp.vel[i*3+2];
        bp.vel[i*3] *= 0.98;
        bp.vel[i*3+1] *= 0.98;
        bp.vel[i*3+2] *= 0.98;
      }
      bp.mesh.geometry.attributes.position.needsUpdate = true;
      bp.mesh.material.opacity = Math.max(0, 1 - bp.time / 2);
    }

    // Smooth camera follow (only when not dragging)
    if (!isDragging) {
      camera.position.x += (mouseTarget.x * 2 - camera.position.x) * 0.01;
      camera.position.y += (mouseTarget.y * 1.5 - camera.position.y) * 0.01;
    }
    camera.lookAt(0, 0, 0);
    renderer.render(scene, camera);
  }

  // ── Interaction ──
  let mouseTarget = { x: 0, y: 0 };

  function getIntersects(event) {
    const rect = renderer.domElement.getBoundingClientRect();
    const x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
    const y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
    mouse.set(x, y);
    raycaster.setFromCamera(mouse, camera);
    const meshes = serviceNodes.filter(s => s.mesh).map(s => s.mesh);
    return raycaster.intersectObjects(meshes);
  }

  function onMouseMove(e) {
    mouseTarget.x = (e.clientX / window.innerWidth) * 2 - 1;
    mouseTarget.y = -(e.clientY / window.innerHeight) * 2 + 1;
    
    if (isDragging) {
      autoRotate = false;
      const dx = e.clientX - previousMouse.x;
      const dy = e.clientY - previousMouse.y;
      if (infinityGroup) {
        infinityGroup.rotation.y += dx * 0.005;
        infinityGroup.rotation.x += dy * 0.005;
      }
      previousMouse.x = e.clientX;
      previousMouse.y = e.clientY;
      return;
    }

    // Hover detection
    const intersects = getIntersects(e);
    if (intersects.length > 0) {
      const hit = intersects[0].object;
      const svc = serviceNodes.find(s => s.mesh === hit);
      if (svc) {
        hoveredService = svc.id;
        showTooltip = true;
        tooltipText = `${svc.name}: ${svc.desc}`;
        tooltipStyle = `left:${e.clientX + 15}px;top:${e.clientY - 10}px`;
        renderer.domElement.style.cursor = "pointer";
        return;
      }
    }
    hoveredService = null;
    showTooltip = false;
    renderer.domElement.style.cursor = "default";
  }

  function onMouseDown(e) {
    isDragging = true;
    previousMouse.x = e.clientX;
    previousMouse.y = e.clientY;
    autoRotate = false;
  }

  function onMouseUp(e) {
    isDragging = false;
    setTimeout(() => { autoRotate = true; }, 3000);
  }

  function onClick(e) {
    const intersects = getIntersects(e);
    if (intersects.length > 0) {
      const hit = intersects[0].object;
      const svc = serviceNodes.find(s => s.mesh === hit);
      if (svc) {
        // Toggle selection
        if (selectedService === svc.id) {
          selectedService = null;
        } else {
          selectedService = svc.id;
          triggerBurst(svc.position.x, svc.position.y, svc.position.z, svc.color);
          addNotif(`✦ ${svc.name}: ${svc.desc}`);
        }
      }
    } else {
      selectedService = null;
    }
  }

  function onTouchStart(e) {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      previousMouse.x = touch.clientX;
      previousMouse.y = touch.clientY;
      isDragging = false;
      autoRotate = false;
    }
  }

  function onTouchMove(e) {
    if (e.touches.length === 1) {
      const touch = e.touches[0];
      if (isDragging) {
        const dx = touch.clientX - previousMouse.x;
        const dy = touch.clientY - previousMouse.y;
        if (infinityGroup) {
          infinityGroup.rotation.y += dx * 0.005;
          infinityGroup.rotation.x += dy * 0.005;
        }
      }
      previousMouse.x = touch.clientX;
      previousMouse.y = touch.clientY;
      isDragging = true;
    }
  }

  function onTouchEnd(e) {
    isDragging = false;
    if (!e.changedTouches) return;
    const touch = e.changedTouches[0];
    // Simulate click on touch end if not dragged
    if (Math.abs(touch.clientX - previousMouse.x) < 10) {
      const rect = renderer.domElement.getBoundingClientRect();
      const ev = new MouseEvent("click", {
        clientX: touch.clientX, clientY: touch.clientY,
        bubbles: true
      });
      renderer.domElement.dispatchEvent(ev);
    }
    setTimeout(() => { autoRotate = true; }, 3000);
  }

  function onResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
  }

  // ── WebSocket ──
  function connectWS() {
    const proto = location.protocol === "https:" ? "wss:" : "ws:";
    try {
      ws = new WebSocket(`${proto}//${location.host}/v1/chat`);
      ws.onopen = () => { status = "conectado"; statusClass = "online"; addNotif("🟢 Sistema conectado"); };
      ws.onclose = () => { status = "desconectado"; statusClass = "offline"; setTimeout(connectWS, 3000); };
      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data);
          if (msg.type === "wakeword.detected") {
            addNotif(`🔮 "${msg.keyword}" detectado`);
            wakeActive = true; setTimeout(() => wakeActive = false, 2000);
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

  // ── System Data ──
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

  // ── Voice ──
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

  <StickerSystem {activeTenant} {audioLevel} />

  <!-- Tooltip flotante -->
  {#if showTooltip}
  <div class="tooltip" style={tooltipStyle}>{tooltipText}</div>
  {/if}

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
        <div class="tenant-select">
          <select bind:value={activeTenant} on:change={(e) => { activeTenant = e.target.value; tenantName = TENANTS[activeTenant]?.name || activeTenant; }}>
            {#each Object.keys(TENANTS) as tid}
              <option value={tid}>{TENANTS[tid].name}</option>
            {/each}
          </select>
        </div>
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

  <!-- Info panel del servicio seleccionado -->
  {#if selectedService}
    {#each SERVICES.filter(s => s.id === selectedService) as svc}
    <div class="info-panel">
      <div class="info-header" style="border-color: #{svc.color.toString(16).padStart(6,'0')}">
        <span class="info-name">{svc.name}</span>
        <button class="info-close" on:click={() => selectedService = null}>✕</button>
      </div>
      <div class="info-body">
        <p>{svc.desc}</p>
        {#if svc.port}
          <p class="info-detail">📍 Puerto: {svc.port}</p>
        {/if}
        <p class="info-detail">📡 Estado: {svc.status}</p>
      </div>
    </div>
    {/each}
  {/if}

  <div class="wake-indicator" class:visible={wakeActive}>
    <span class="dot"></span>
    <span>🔮 Escuchando "Hey Jarvis"</span>
  </div>

  <button class="voice-btn" class:recording={voiceActive} on:click={toggleVoice}>
    {voiceActive ? "⏹" : "🎤"}
  </button>

  <button class="avatar-btn" on:click={() => showAvatar = !showAvatar} title="Avatar 3D">
    🧑
  </button>

  <div class="notifications">
    {#each notifications as notif}
      <div class="notif">{notif.text}</div>
    {/each}
  </div>

  <!-- Avatar Overlay -->
  {#if showAvatar}
  <div class="avatar-overlay">
    <div class="avatar-header">
      <h2>🧑 Avatar 3D — César Holguín</h2>
      <button class="close-btn" on:click={() => showAvatar = false}>✕</button>
    </div>
    <div class="avatar-body">
      <AvatarPage />
    </div>
  </div>
  {/if}

  <!-- Hint flotante -->
  <div class="hint">
    Arrastra para rotar ∞ · Click en nodos · 🧑 Avatar
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

  .tooltip {
    position: fixed; z-index: 50;
    background: rgba(17,19,30,0.9); backdrop-filter: blur(10px);
    border: 1px solid rgba(200,146,75,0.3); border-radius: 8px;
    padding: 8px 14px; font-size: 12px; color: #E0AD6E;
    pointer-events: none; white-space: nowrap;
    animation: fadeIn 0.2s;
  }

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
    display: flex; flex-direction: column; justify-content: space-between; padding: 20px 28px;
  }
  .top-bar { display: flex; align-items: center; justify-content: space-between; pointer-events: auto; }
  .brand h1 { font-size: 13px; font-weight: 400; letter-spacing: 4px; text-transform: uppercase; color: rgba(255,255,255,0.4); }
  .brand h1 span { color: #C8924B; }
  .ver { font-size: 10px; color: rgba(255,255,255,0.2); letter-spacing: 2px; margin-top: 2px; }
  .status-bar { display: flex; align-items: center; gap: 12px; }
  .dot { width: 8px; height: 8px; border-radius: 50%; }
  .dot.online { background: #00e676; box-shadow: 0 0 12px #00e676; animation: pulse 1.5s infinite; }
  .dot.offline { background: #ff3355; box-shadow: 0 0 12px #ff3355; }
  @keyframes pulse { 0%,100% { opacity: 1; } 50% { opacity: 0.4; } }
  .label { font-size: 11px; color: rgba(237,240,247,0.5); letter-spacing: 1px; text-transform: uppercase; }
  .time { font-size: 11px; color: rgba(237,240,247,0.5); letter-spacing: 1px; font-variant-numeric: tabular-nums; }
  .tenant-select select {
    background: rgba(17,19,30,0.6); border: 1px solid rgba(255,255,255,0.08);
    color: rgba(237,240,247,0.6); font-size: 10px; padding: 4px 8px;
    border-radius: 6px; font-family: inherit; cursor: pointer;
    letter-spacing: 0.5px; max-width: 140px;
  }
  .tenant-select select:hover { border-color: rgba(200,146,75,0.2); }

  .center { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); text-align: center; pointer-events: none; z-index: 5; }
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

  .info-panel {
    position: fixed; bottom: 180px; left: 28px; z-index: 20;
    background: rgba(17,19,30,0.85); backdrop-filter: blur(20px);
    border: 1px solid; border-radius: 12px; padding: 0;
    min-width: 240px; pointer-events: auto;
    animation: slideUp 0.3s ease;
  }
  @keyframes slideUp { from { transform: translateY(20px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
  .info-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 12px 16px; border-bottom: 1px solid rgba(255,255,255,0.06);
    font-weight: 600; font-size: 14px;
  }
  .info-close {
    background: none; border: none; color: rgba(255,255,255,0.3);
    font-size: 16px; cursor: pointer; padding: 4px 8px; border-radius: 4px;
  }
  .info-close:hover { background: rgba(255,255,255,0.1); color: #fff; }
  .info-body { padding: 14px 16px; font-size: 13px; color: rgba(237,240,247,0.8); line-height: 1.5; }
  .info-detail { font-size: 11px; color: rgba(237,240,247,0.4); margin-top: 6px; }

  .wake-indicator {
    position: fixed; bottom: 170px; right: 28px; z-index: 20;
    display: none; align-items: center; gap: 8px;
    background: rgba(17,19,30,0.8); backdrop-filter: blur(12px);
    border: 1px solid rgba(200,146,75,0.2); border-radius: 20px;
    padding: 8px 16px; font-size: 11px; color: #E0AD6E; pointer-events: none;
  }
  .wake-indicator.visible { display: flex; }
  .wake-indicator .dot { width: 6px; height: 6px; background: #C8924B; animation: pulse-dot 1.5s infinite; }
  @keyframes pulse-dot { 0%,100% { opacity: 0.3; } 50% { opacity: 1; } }

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
    animation: fadeIn 0.3s; max-width: 280px; pointer-events: auto;
  }
  @keyframes fadeIn { from { transform: translateX(40px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }

  .avatar-btn {
    position: fixed; bottom: 100px; right: 96px; z-index: 20;
    width: 48px; height: 48px; border-radius: 50%;
    background: rgba(17,19,30,0.7); backdrop-filter: blur(12px);
    border: 1px solid rgba(255,255,255,0.1); color: var(--text-dim);
    font-size: 20px; cursor: pointer; transition: 0.3s; pointer-events: auto;
    display: flex; align-items: center; justify-content: center;
  }
  .avatar-btn:hover { border-color: var(--gold); background: rgba(200,146,75,0.1); }

  .avatar-overlay {
    position: fixed; inset: 0; z-index: 100;
    background: rgba(8,9,15,0.95);
    backdrop-filter: blur(20px);
    display: flex; flex-direction: column;
    animation: fadeIn 0.3s;
  }
  .avatar-header {
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 24px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }
  .avatar-header h2 {
    font-size: 14px; font-weight: 500;
    color: rgba(237,240,247,0.8);
    letter-spacing: 1px;
  }
  .close-btn {
    background: none; border: none; color: rgba(237,240,247,0.3);
    font-size: 20px; cursor: pointer; padding: 4px 12px;
    border-radius: 6px;
  }
  .close-btn:hover { background: rgba(255,255,255,0.05); color: #fff; }
  .avatar-body {
    flex: 1;
    overflow: hidden;
  }

  .hint {
    position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
    z-index: 10; font-size: 10px; color: rgba(237,240,247,0.15);
    letter-spacing: 1px; pointer-events: none; text-align: center;
  }

  @media(max-width: 768px) {
    .panels { grid-template-columns: 1fr 1fr; gap: 8px; }
    .hud { padding: 12px 16px; }
    .panel { padding: 10px 12px; }
    .value { font-size: 18px; }
    .info-panel { left: 16px; right: 16px; bottom: 160px; min-width: auto; }
  }
</style>
