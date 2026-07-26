<script>
  import { onMount } from "svelte";
  import Avatar3D from "./Avatar3D.svelte";
  import CameraCapture from "./CameraCapture.svelte";

  let avatarComponent;
  let cameraComponent;
  let avatarImage = null;
  let audioLevel = 0;
  let activeTab = "avatar";
  let showCamera = false;
  let capturedPhotos = [];
  let showScreenCapture = false;
  let gestureLabel = "Idle";

  // Simulated audio level (replace with real WebSocket audio level)
  let audioInterval;
  onMount(() => {
    audioInterval = setInterval(() => {
      audioLevel = Math.random() * 0.3;
    }, 200);
    return () => clearInterval(audioInterval);
  });

  function handlePhotoCaptured(e) {
    avatarImage = e.detail.image;
    capturedPhotos = [...capturedPhotos, e.detail.image];
    showCamera = false;
  }

  function handleGesture(gesture) {
    if (avatarComponent) {
      avatarComponent.setGesture(gesture);
      const labels = { idle: "😐 Reposo", talk: "🗣️ Hablando", point: "☝️ Señalando", wave: "👋 Saludando", think: "🤔 Pensando", explain: "🙌 Explicando" };
      gestureLabel = labels[gesture] || gesture;
    }
  }

  async function captureScreen() {
    try {
      const stream = await navigator.mediaDevices.getDisplayMedia({ video: true });
      const track = stream.getVideoTracks()[0];
      const imageCapture = new ImageCapture(track);
      const bitmap = await imageCapture.grabFrame();
      const canvas = document.createElement("canvas");
      canvas.width = bitmap.width;
      canvas.height = bitmap.height;
      const ctx = canvas.getContext("2d");
      ctx.drawImage(bitmap, 0, 0);
      const dataUrl = canvas.toDataURL("image/png");
      track.stop();
      capturedPhotos = [...capturedPhotos, dataUrl];
      avatarImage = dataUrl;
      showScreenCapture = false;
    } catch(e) {
      alert("❌ Screenshot cancelado o no disponible");
    }
  }
</script>

<div class="avatar-page">
  <!-- Left: Avatar 3D -->
  <div class="avatar-view">
    <Avatar3D bind:this={avatarComponent} {avatarImage} {audioLevel} size={2.5} />
    
    <!-- Gesture controls -->
    <div class="gesture-controls">
      {#each ["idle", "talk", "point", "wave", "think", "explain"] as gesture}
        <button class="gesture-btn" on:click={() => handleGesture(gesture)} title={gesture}>
          {gesture === "idle" && "😐"}
          {gesture === "talk" && "🗣️"}
          {gesture === "point" && "☝️"}
          {gesture === "wave" && "👋"}
          {gesture === "think" && "🤔"}
          {gesture === "explain" && "🙌"}
        </button>
      {/each}
    </div>
    <div class="gesture-label">{gestureLabel}</div>
  </div>

  <!-- Right: Controls -->
  <div class="controls-panel">
    <div class="panel-tabs">
      <button class="tab" class:active={activeTab === "avatar"} on:click={() => activeTab = "avatar"}>🎭 Avatar</button>
      <button class="tab" class:active={activeTab === "camera"} on:click={() => { activeTab = "camera"; showCamera = true; }}>📷 Foto</button>
      <button class="tab" class:active={activeTab === "gallery"} on:click={() => activeTab = "gallery"}>🖼️ Galería</button>
    </div>

    <div class="panel-content">
      {#if activeTab === "avatar"}
        <div class="section">
          <h3>🎭 Apariencia del Avatar</h3>
          <div class="avatar-options">
            <button class="option-btn" class:selected={!avatarImage} on:click={() => avatarImage = null}>
              <span class="option-icon">🤖</span>
              <span>Geométrico</span>
            </button>
            <button class="option-btn" class:selected={avatarImage !== null} on:click={() => showCamera = true}>
              <span class="option-icon">🧑</span>
              <span>Foto real</span>
            </button>
          </div>
        </div>

        <div class="section">
          <h3>🎬 Gestos del Avatar</h3>
          <div class="gesture-grid">
            {#each [
              {id:"idle", icon:"😐", label:"Reposo"},
              {id:"talk", icon:"🗣️", label:"Hablar"},
              {id:"point", icon:"☝️", label:"Señalar"},
              {id:"wave", icon:"👋", label:"Saludar"},
              {id:"think", icon:"🤔", label:"Pensar"},
              {id:"explain", icon:"🙌", label:"Explicar"},
            ] as g}
              <button class="gesture-card" on:click={() => handleGesture(g.id)}>
                <span class="g-icon">{g.icon}</span>
                <span class="g-label">{g.label}</span>
              </button>
            {/each}
          </div>
        </div>

        <div class="section">
          <h3>📸 Captura de pantalla</h3>
          <button class="btn primary" on:click={captureScreen}>
            🖥️ Capturar pantalla
          </button>
        </div>
      {/if}

      {#if activeTab === "camera" || showCamera}
        <div class="section camera-section">
          <CameraCapture 
            bind:this={cameraComponent}
            on:photo:captured={handlePhotoCaptured}
            on:photo:confirm={(e) => handlePhotoCaptured(e)}
          />
        </div>
      {/if}

      {#if activeTab === "gallery"}
        <div class="section">
          <h3>🖼️ Galería de fotos ({capturedPhotos.length})</h3>
          {#if capturedPhotos.length === 0}
            <p class="empty">Aún no hay fotos. Tómate una selfie o captura la pantalla.</p>
          {:else}
            <div class="gallery-grid">
              {#each capturedPhotos as photo, i}
                <div class="gallery-item">
                  <img src={photo} alt={`Photo ${i+1}`} on:click={() => avatarImage = photo} />
                  <button class="gallery-use" on:click={() => avatarImage = photo}>Usar</button>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <div class="section">
          <h3>📤 Subir foto</h3>
          <label class="btn upload">
            📁 Seleccionar archivo
            <input type="file" accept="image/*" hidden on:change={(e) => {
              if (e.target.files[0]) {
                const reader = new FileReader();
                reader.onload = (ev) => {
                  const img = ev.target.result;
                  avatarImage = img;
                  capturedPhotos = [...capturedPhotos, img];
                };
                reader.readAsDataURL(e.target.files[0]);
              }
            }} />
          </label>
        </div>
      {/if}
    </div>
  </div>
</div>

<style>
  .avatar-page {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    height: 100%;
    padding: 16px;
  }

  .avatar-view {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
    background: rgba(17,19,30,0.4);
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.04);
    padding: 16px;
    height: 100%;
    min-height: 400px;
  }
  .avatar-view :global(.avatar-wrapper) {
    flex: 1;
    min-height: 300px;
  }

  .gesture-controls {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .gesture-btn {
    width: 40px; height: 40px;
    border-radius: 50%;
    border: 1px solid rgba(255,255,255,0.08);
    background: rgba(255,255,255,0.03);
    color: #edf0f7;
    font-size: 18px;
    cursor: pointer;
    transition: 0.2s;
  }
  .gesture-btn:hover {
    background: rgba(200,146,75,0.15);
    border-color: rgba(200,146,75,0.3);
    transform: scale(1.1);
  }
  .gesture-label {
    font-size: 11px;
    color: rgba(237,240,247,0.4);
    letter-spacing: 1px;
  }

  .controls-panel {
    background: rgba(17,19,30,0.6);
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.04);
    overflow: hidden;
    display: flex;
    flex-direction: column;
  }

  .panel-tabs {
    display: flex;
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }
  .tab {
    flex: 1;
    padding: 10px;
    background: none;
    border: none;
    color: rgba(237,240,247,0.4);
    font-size: 12px;
    cursor: pointer;
    transition: 0.2s;
    font-family: inherit;
    letter-spacing: 1px;
  }
  .tab.active {
    color: #E0AD6E;
    border-bottom: 2px solid #C8924B;
  }
  .tab:hover { color: #edf0f7; }

  .panel-content {
    flex: 1;
    overflow-y: auto;
    padding: 16px;
  }

  .section {
    margin-bottom: 20px;
  }
  .section h3 {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: rgba(237,240,247,0.4);
    margin-bottom: 10px;
    font-weight: 500;
  }

  .avatar-options {
    display: flex;
    gap: 8px;
  }
  .option-btn {
    flex: 1;
    padding: 12px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.06);
    background: rgba(255,255,255,0.03);
    color: #edf0f7;
    cursor: pointer;
    transition: 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    font-family: inherit;
    font-size: 12px;
  }
  .option-btn:hover { background: rgba(255,255,255,0.06); }
  .option-btn.selected {
    border-color: rgba(200,146,75,0.3);
    background: rgba(200,146,75,0.08);
  }
  .option-icon { font-size: 28px; }

  .gesture-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 6px;
  }
  .gesture-card {
    padding: 10px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.04);
    background: rgba(255,255,255,0.02);
    color: #edf0f7;
    cursor: pointer;
    transition: 0.2s;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    font-family: inherit;
    font-size: 11px;
  }
  .gesture-card:hover {
    background: rgba(200,146,75,0.08);
    border-color: rgba(200,146,75,0.2);
  }
  .g-icon { font-size: 22px; }
  .g-label { color: rgba(237,240,247,0.6); }

  .gallery-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
  }
  .gallery-item {
    position: relative;
    border-radius: 8px;
    overflow: hidden;
    aspect-ratio: 1;
  }
  .gallery-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    cursor: pointer;
  }
  .gallery-item:hover .gallery-use {
    opacity: 1;
  }
  .gallery-use {
    position: absolute;
    bottom: 4px;
    left: 50%;
    transform: translateX(-50%);
    padding: 4px 12px;
    border-radius: 12px;
    border: none;
    background: rgba(200,146,75,0.8);
    color: #fff;
    font-size: 11px;
    cursor: pointer;
    opacity: 0;
    transition: 0.2s;
    backdrop-filter: blur(8px);
  }

  .empty {
    font-size: 12px;
    color: rgba(237,240,247,0.3);
    text-align: center;
    padding: 20px;
  }

  .btn {
    padding: 8px 16px;
    border-radius: 8px;
    border: 1px solid rgba(255,255,255,0.1);
    background: rgba(255,255,255,0.05);
    color: #edf0f7;
    font-size: 12px;
    cursor: pointer;
    transition: 0.2s;
    font-family: inherit;
    display: inline-flex;
    align-items: center;
    gap: 6px;
  }
  .btn:hover { background: rgba(255,255,255,0.1); }
  .btn.primary {
    background: rgba(200,146,75,0.2);
    border-color: rgba(200,146,75,0.3);
    color: #E0AD6E;
  }
  .btn.primary:hover { background: rgba(200,146,75,0.3); }
  .btn.upload { cursor: pointer; }

  .camera-section {
    height: 100%;
    min-height: 300px;
  }

  @media(max-width: 768px) {
    .avatar-page {
      grid-template-columns: 1fr;
      padding: 8px;
    }
    .avatar-view { min-height: 300px; }
  }
</style>
