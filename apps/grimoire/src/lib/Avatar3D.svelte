<script>
  import { onMount, onDestroy, createEventDispatcher } from "svelte";
  import * as THREE from "three";

  export let avatarImage = null; // base64 or URL
  export let size = 2.0;
  export let audioLevel = 0; // 0-1 for voice reactivity

  const dispatch = createEventDispatcher();
  let container;
  let scene, camera, renderer;
  let avatarGroup, headMesh, bodyMesh, leftArm, rightArm;
  let particles;
  let clock = 0;
  let animId;
  let isDragging = false;
  let prevMouse = { x: 0, y: 0 };
  let autoRotate = true;
  let currentGesture = "idle";
  let gestureTime = 0;

  // Face mapping for expressions
  let expression = "neutral";
  const EXPRESSIONS = ["neutral", "happy", "thinking", "speaking", "listening"];

  onMount(() => {
    initScene();
    animate();
  });

  onDestroy(() => {
    if (animId) cancelAnimationFrame(animId);
    if (renderer) {
      renderer.dispose();
      if (renderer.domElement.parentNode) renderer.domElement.parentNode.removeChild(renderer.domElement);
    }
  });

  function initScene() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(45, container.clientWidth / container.clientHeight, 0.1, 100);
    camera.position.set(0, 1.5, 4);
    camera.lookAt(0, 1, 0);

    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setClearColor(0x000000, 0);
    container.appendChild(renderer.domElement);

    // Lights
    const ambient = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambient);
    const key = new THREE.DirectionalLight(0xffffff, 1.0);
    key.position.set(2, 3, 4);
    scene.add(key);
    const fill = new THREE.DirectionalLight(0x8888ff, 0.3);
    fill.position.set(-2, 1, -2);
    scene.add(fill);
    const rim = new THREE.DirectionalLight(0xffeedd, 0.4);
    rim.position.set(0, -1, -3);
    scene.add(rim);

    buildAvatar();
    buildParticles();
    
    window.addEventListener("resize", onResize);
    renderer.domElement.addEventListener("mousedown", onMouseDown);
    renderer.domElement.addEventListener("mousemove", onMouseMove);
    renderer.domElement.addEventListener("mouseup", onMouseUp);
    renderer.domElement.addEventListener("touchstart", onTouchStart, { passive: true });
    renderer.domElement.addEventListener("touchmove", onTouchMove, { passive: true });
    renderer.domElement.addEventListener("touchend", onTouchEnd, { passive: true });
  }

  function buildAvatar() {
    avatarGroup = new THREE.Group();
    scene.add(avatarGroup);

    // ── Load avatar texture ──
    const textureLoader = new THREE.TextureLoader();
    let avatarTexture = null;
    
    if (avatarImage) {
      if (avatarImage.startsWith("data:") || avatarImage.startsWith("http")) {
        avatarTexture = textureLoader.load(avatarImage);
      }
    }

    // If no image, create a geometric face (cyberpunk style)
    const faceGroup = new THREE.Group();

    // Head - geometric crystal
    const headGeo = new THREE.IcosahedronGeometry(0.65, 1);
    const headMat = new THREE.MeshPhysicalMaterial({
      color: avatarTexture ? 0xffffff : 0xC8924B,
      map: avatarTexture || null,
      metalness: avatarTexture ? 0.0 : 0.3,
      roughness: avatarTexture ? 0.8 : 0.4,
      transparent: true,
      opacity: 0.95,
      wireframe: !avatarTexture,
      emissive: !avatarTexture ? 0xC8924B : 0x000000,
      emissiveIntensity: !avatarTexture ? 0.1 : 0,
    });
    headMesh = new THREE.Mesh(headGeo, headMat);
    headMesh.position.y = 1.6;
    faceGroup.add(headMesh);

    // Inner glow for geometric avatar
    if (!avatarTexture) {
      const innerGeo = new THREE.IcosahedronGeometry(0.5, 0);
      const innerMat = new THREE.MeshBasicMaterial({
        color: 0xE0AD6E,
        transparent: true,
        opacity: 0.15,
        wireframe: true,
      });
      const inner = new THREE.Mesh(innerGeo, innerMat);
      inner.position.y = 1.6;
      faceGroup.add(inner);
    }

    // Eyes (two small spheres)
    const eyeMat = new THREE.MeshBasicMaterial({ color: 0x00d4ff });
    [-0.2, 0.2].forEach(x => {
      const eye = new THREE.Mesh(new THREE.SphereGeometry(0.06, 8, 8), eyeMat);
      eye.position.set(x, 1.7, 0.55);
      faceGroup.add(eye);
    });

    // Eye glow
    [-0.2, 0.2].forEach(x => {
      const glow = new THREE.Mesh(
        new THREE.SphereGeometry(0.1, 8, 8),
        new THREE.MeshBasicMaterial({ color: 0x00d4ff, transparent: true, opacity: 0.15 })
      );
      glow.position.set(x, 1.7, 0.55);
      faceGroup.add(glow);
    });

    // Mouth line
    const mouthPoints = [
      new THREE.Vector3(-0.15, 1.45, 0.6),
      new THREE.Vector3(0, 1.4, 0.65),
      new THREE.Vector3(0.15, 1.45, 0.6),
    ];
    const mouthGeo = new THREE.BufferGeometry().setFromPoints(mouthPoints);
    const mouthMat = new THREE.LineBasicMaterial({ color: 0xE0AD6E, transparent: true, opacity: 0.6 });
    const mouth = new THREE.Line(mouthGeo, mouthMat);
    faceGroup.add(mouth);

    // Body (torso)
    const bodyGeo = new THREE.CylinderGeometry(0.5, 0.7, 1.2, 8);
    const bodyMat = new THREE.MeshPhysicalMaterial({
      color: 0x1a1a2e,
      metalness: 0.2,
      roughness: 0.6,
      transparent: true,
      opacity: 0.9,
    });
    bodyMesh = new THREE.Mesh(bodyGeo, bodyMat);
    bodyMesh.position.y = 0.8;
    faceGroup.add(bodyMesh);

    // Chest plate (cyberpunk detail)
    const plateGeo = new THREE.BoxGeometry(0.4, 0.3, 0.05);
    const plateMat = new THREE.MeshBasicMaterial({
      color: 0xC8924B,
      transparent: true,
      opacity: 0.3,
    });
    const plate = new THREE.Mesh(plateGeo, plateMat);
    plate.position.set(0, 0.9, 0.55);
    faceGroup.add(plate);

    // Arms
    const armMat = new THREE.MeshPhysicalMaterial({
      color: 0x1a1a2e,
      metalness: 0.1,
      roughness: 0.7,
      transparent: true,
      opacity: 0.9,
    });

    // Left arm
    const leftArmGroup = new THREE.Group();
    const leftArmUpper = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 0.5, 6), armMat);
    leftArmUpper.position.y = -0.25;
    leftArmGroup.add(leftArmUpper);
    leftArmGroup.position.set(-0.65, 1.3, 0);
    leftArmGroup.rotation.z = 0.3;
    faceGroup.add(leftArmGroup);
    leftArm = leftArmGroup;

    // Right arm
    const rightArmGroup = new THREE.Group();
    const rightArmUpper = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.1, 0.5, 6), armMat);
    rightArmUpper.position.y = -0.25;
    rightArmGroup.add(rightArmUpper);
    rightArmGroup.position.set(0.65, 1.3, 0);
    rightArmGroup.rotation.z = -0.3;
    faceGroup.add(rightArmGroup);
    rightArm = rightArmGroup;

    // Shoulder pads
    [leftArmGroup, rightArmGroup].forEach((arm, i) => {
      const pad = new THREE.Mesh(
        new THREE.SphereGeometry(0.1, 6, 6),
        new THREE.MeshBasicMaterial({ color: 0xC8924B, transparent: true, opacity: 0.5 })
      );
      pad.position.set(0, 0.2, 0);
      arm.add(pad);
    });

    avatarGroup.add(faceGroup);
  }

  function buildParticles() {
    const count = 200;
    const geo = new THREE.BufferGeometry();
    const pos = new Float32Array(count * 3);
    const sizes = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      const radius = 2 + Math.random() * 3;
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      pos[i*3] = radius * Math.sin(phi) * Math.cos(theta);
      pos[i*3+1] = radius * Math.sin(phi) * Math.sin(theta) + 1;
      pos[i*3+2] = radius * Math.cos(phi);
      sizes[i] = 0.02 + Math.random() * 0.04;
    }
    geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      color: 0xC8924B, size: 0.03, transparent: true,
      opacity: 0.3, blending: THREE.AdditiveBlending, depthWrite: false,
    });
    particles = new THREE.Points(geo, mat);
    scene.add(particles);
  }

  // ── Gestures System ──
  function updateGestures(time) {
    if (!avatarGroup) return;

    // Random gesture switching
    gestureTime += 0.016;
    if (gestureTime > 3 + Math.random() * 4) {
      gestureTime = 0;
      const gestures = ["idle", "talk", "point", "wave", "think", "explain"];
      currentGesture = gestures[Math.floor(Math.random() * gestures.length)];
    }

    // Idle breathing
    const breathe = Math.sin(time * 2) * 0.02;
    avatarGroup.position.y = breathe;

    // Head movement
    if (headMesh) {
      headMesh.rotation.x = Math.sin(time * 0.5) * 0.05;
      headMesh.rotation.y = Math.sin(time * 0.3) * 0.08;
    }

    // Arm animations based on gesture
    if (leftArm && rightArm) {
      switch (currentGesture) {
        case "idle":
          leftArm.rotation.z = 0.3 + Math.sin(time * 1.5) * 0.05;
          rightArm.rotation.z = -0.3 + Math.sin(time * 1.5 + 1) * 0.05;
          leftArm.rotation.x = 0;
          rightArm.rotation.x = 0;
          break;
        case "talk":
          // Arms move like talking
          leftArm.rotation.z = 0.3 + Math.sin(time * 4) * 0.2;
          rightArm.rotation.z = -0.3 + Math.sin(time * 4 + 2) * 0.15;
          leftArm.rotation.x = Math.sin(time * 3) * 0.1;
          rightArm.rotation.x = Math.sin(time * 3 + 1) * 0.1;
          expression = "speaking";
          break;
        case "point":
          // Right arm points forward
          rightArm.rotation.x = -1.2;
          rightArm.rotation.z = -0.5;
          leftArm.rotation.z = 0.5;
          leftArm.rotation.x = 0.2;
          expression = "thinking";
          break;
        case "wave":
          // Waving
          rightArm.rotation.x = -0.5;
          rightArm.rotation.z = -0.8 + Math.sin(time * 3) * 0.3;
          leftArm.rotation.z = 0.3;
          expression = "happy";
          break;
        case "explain":
          // Both arms open
          leftArm.rotation.z = 0.8 + Math.sin(time * 2) * 0.1;
          rightArm.rotation.z = -0.8 + Math.sin(time * 2 + 1) * 0.1;
          leftArm.rotation.x = -0.3;
          rightArm.rotation.x = -0.3;
          expression = "thinking";
          break;
        case "think":
          // Hand to chin
          rightArm.rotation.x = -1.5;
          rightArm.rotation.z = -0.3;
          leftArm.rotation.z = 0.6;
          leftArm.rotation.x = 0.4;
          expression = "thinking";
          break;
      }
    }

    // Audio reactivity
    if (audioLevel > 0.05) {
      if (headMesh) {
        headMesh.scale.x = 1 + audioLevel * 0.05;
        headMesh.scale.y = 1 + audioLevel * 0.03;
      }
      // Body pulses with audio
      if (bodyMesh) {
        bodyMesh.material.emissive = new THREE.Color(0xC8924B);
        bodyMesh.material.emissiveIntensity = audioLevel * 0.3;
      }
      expression = "speaking";
    } else {
      if (bodyMesh) {
        bodyMesh.material.emissive = new THREE.Color(0x000000);
        bodyMesh.material.emissiveIntensity = 0;
      }
    }

    // Expression changes reflected in eye glow
    const eyeGlows = [];
    avatarGroup.children.forEach(child => {
      child.children?.forEach(c => {
        if (c.material?.color?.getHex() === 0x00d4ff && c.type === "Mesh" && c.geometry.type === "SphereGeometry" && c.geometry.parameters.radius > 0.08) {
          eyeGlows.push(c);
        }
      });
    });
    eyeGlows.forEach(g => {
      switch(expression) {
        case "happy": g.material.color.setHex(0x00ff88); break;
        case "thinking": g.material.color.setHex(0xff8800); break;
        case "speaking": g.material.color.setHex(0x00d4ff); break;
        default: g.material.color.setHex(0x00d4ff);
      }
      g.material.opacity = 0.15 + Math.sin(time * 2) * 0.08;
    });
  }

  function animate() {
    animId = requestAnimationFrame(animate);
    clock += 0.016;

    updateGestures(clock);

    // Rotate particle field
    if (particles) {
      particles.rotation.y += 0.001;
      particles.rotation.x = Math.sin(clock * 0.02) * 0.05;
    }

    // Auto-rotate avatar
    if (autoRotate && avatarGroup) {
      avatarGroup.rotation.y += 0.005;
    }

    renderer.render(scene, camera);
  }

  // ── Drag to rotate ──
  function onMouseDown(e) {
    isDragging = true;
    prevMouse.x = e.clientX;
    prevMouse.y = e.clientY;
    autoRotate = false;
  }

  function onMouseMove(e) {
    if (isDragging && avatarGroup) {
      const dx = e.clientX - prevMouse.x;
      const dy = e.clientY - prevMouse.y;
      avatarGroup.rotation.y += dx * 0.01;
      avatarGroup.rotation.x += dy * 0.005;
      prevMouse.x = e.clientX;
      prevMouse.y = e.clientY;
    }
  }

  function onMouseUp() {
    isDragging = false;
    dispatch("interact", { action: "rotate" });
    setTimeout(() => { autoRotate = true; }, 3000);
  }

  function onTouchStart(e) {
    if (e.touches.length === 1) {
      prevMouse.x = e.touches[0].clientX;
      prevMouse.y = e.touches[0].clientY;
      isDragging = true;
      autoRotate = false;
    }
  }

  function onTouchMove(e) {
    if (isDragging && e.touches.length === 1 && avatarGroup) {
      const dx = e.touches[0].clientX - prevMouse.x;
      const dy = e.touches[0].clientY - prevMouse.y;
      avatarGroup.rotation.y += dx * 0.01;
      avatarGroup.rotation.x += dy * 0.005;
      prevMouse.x = e.touches[0].clientX;
      prevMouse.y = e.touches[0].clientY;
    }
  }

  function onTouchEnd() {
    isDragging = false;
    setTimeout(() => { autoRotate = true; }, 3000);
  }

  function onResize() {
    if (!container) return;
    const w = container.clientWidth;
    const h = container.clientHeight;
    camera.aspect = w / h;
    camera.updateProjectionMatrix();
    renderer.setSize(w, h);
  }

  // Expose method to trigger gestures
  export function setGesture(gesture) {
    currentGesture = gesture;
    gestureTime = 0;
  }

  export function setExpression(expr) {
    if (EXPRESSIONS.includes(expr)) expression = expr;
  }
</script>

<div class="avatar-wrapper" bind:this={container}>
  <!-- Nombre y estatus -->
  <div class="avatar-tag">
    <span class="tag-dot"></span>
    <span>César Holguín · AztroTech</span>
  </div>
</div>

<style>
  .avatar-wrapper {
    width: 100%;
    height: 100%;
    position: relative;
    border-radius: 16px;
    overflow: hidden;
    background: radial-gradient(ellipse at center, rgba(200,146,75,0.03) 0%, transparent 70%);
  }
  .avatar-tag {
    position: absolute;
    bottom: 12px;
    left: 50%;
    transform: translateX(-50%);
    display: flex;
    align-items: center;
    gap: 8px;
    background: rgba(17,19,30,0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(200,146,75,0.2);
    border-radius: 20px;
    padding: 6px 16px;
    font-size: 11px;
    color: #E0AD6E;
    pointer-events: none;
    white-space: nowrap;
    z-index: 2;
  }
  .tag-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00e676;
    animation: pulse 1.5s infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.3; }
  }
</style>
