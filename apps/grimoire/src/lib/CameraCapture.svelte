<script>
  import { createEventDispatcher } from "svelte";

  export let facingMode = "user"; // "user" or "environment"
  
  const dispatch = createEventDispatcher();
  let videoEl, canvasEl;
  let stream = null;
  let isActive = false;
  let hasPermission = false;
  let capturedImage = null;
  let errorMsg = "";

  export async function startCamera() {
    if (isActive) return;
    try {
      stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode, width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
      if (videoEl) {
        videoEl.srcObject = stream;
        await videoEl.play();
      }
      isActive = true;
      hasPermission = true;
      errorMsg = "";
      dispatch("camera:started");
    } catch (e) {
      errorMsg = "❌ No se pudo acceder a la cámara: " + e.message;
      hasPermission = false;
    }
  }

  export function stopCamera() {
    if (stream) {
      stream.getTracks().forEach(t => t.stop());
      stream = null;
    }
    if (videoEl) videoEl.srcObject = null;
    isActive = false;
  }

  export function capturePhoto() {
    if (!videoEl || !isActive) return;
    const w = videoEl.videoWidth || 640;
    const h = videoEl.videoHeight || 480;
    canvasEl.width = w;
    canvasEl.height = h;
    const ctx = canvasEl.getContext("2d");
    ctx.drawImage(videoEl, 0, 0, w, h);
    capturedImage = canvasEl.toDataURL("image/jpeg", 0.8);
    dispatch("photo:captured", { image: capturedImage });
    return capturedImage;
  }

  export function flipCamera() {
    stopCamera();
    facingMode = facingMode === "user" ? "environment" : "user";
    setTimeout(() => startCamera(), 300);
  }

  export function getImage() {
    return capturedImage;
  }

  export function loadFromFile(file) {
    return new Promise((resolve) => {
      if (!file.type.startsWith("image/")) {
        errorMsg = "❌ Solo imágenes";
        resolve(null);
        return;
      }
      const reader = new FileReader();
      reader.onload = (e) => {
        capturedImage = e.target.result;
        dispatch("photo:captured", { image: capturedImage });
        resolve(capturedImage);
      };
      reader.readAsDataURL(file);
    });
  }

  export function clear() {
    capturedImage = null;
    errorMsg = "";
  }

  export function switchFacing() {
    flipCamera();
  }
</script>

<div class="camera-container">
  {#if capturedImage}
    <div class="preview">
      <img src={capturedImage} alt="Captured" />
      <div class="preview-actions">
        <button class="btn" on:click={() => { capturedImage = null; dispatch("photo:cleared"); }}>✕ Descartar</button>
        <button class="btn primary" on:click={() => dispatch("photo:confirm", { image: capturedImage })}>✓ Usar</button>
      </div>
    </div>
  {:else if isActive}
    <div class="viewfinder">
      <video bind:this={videoEl} autoplay playsinline muted></video>
      <div class="viewfinder-actions">
        <button class="btn" on:click={flipCamera}>🔄 Girar</button>
        <button class="btn capture" on:click={capturePhoto}>📸</button>
        <button class="btn" on:click={stopCamera}>✕ Cerrar</button>
      </div>
    </div>
  {:else}
    <div class="placeholder">
      <div class="placeholder-icon">📷</div>
      <p class="placeholder-text">Tómate una selfie o sube una foto</p>
      {#if errorMsg}
        <p class="error">{errorMsg}</p>
      {/if}
      <div class="placeholder-actions">
        <button class="btn primary" on:click={startCamera}>📸 Abrir cámara</button>
        <label class="btn upload">
          📁 Subir foto
          <input type="file" accept="image/*" hidden on:change={(e) => {
            if (e.target.files[0]) loadFromFile(e.target.files[0]);
          }} />
        </label>
      </div>
    </div>
  {/if}
  <canvas bind:this={canvasEl} hidden></canvas>
</div>

<style>
  .camera-container {
    width: 100%;
    height: 100%;
    border-radius: 12px;
    overflow: hidden;
    background: rgba(0,0,0,0.3);
    position: relative;
  }
  .viewfinder, .preview, .placeholder {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
  }
  video, .preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 12px;
  }
  .viewfinder-actions, .preview-actions, .placeholder-actions {
    display: flex;
    gap: 8px;
    margin-top: 10px;
    flex-wrap: wrap;
    justify-content: center;
  }
  .placeholder {
    gap: 12px;
    padding: 20px;
  }
  .placeholder-icon {
    font-size: 48px;
    opacity: 0.3;
  }
  .placeholder-text {
    font-size: 12px;
    color: rgba(237,240,247,0.5);
    text-align: center;
  }
  .error {
    font-size: 11px;
    color: #ff3355;
    text-align: center;
    max-width: 280px;
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
    gap: 4px;
  }
  .btn:hover { background: rgba(255,255,255,0.1); }
  .btn.primary {
    background: rgba(200,146,75,0.2);
    border-color: rgba(200,146,75,0.3);
    color: #E0AD6E;
  }
  .btn.primary:hover { background: rgba(200,146,75,0.3); }
  .btn.capture {
    width: 56px; height: 56px;
    border-radius: 50%;
    background: linear-gradient(135deg, #C8924B, #c0603a);
    border: none;
    font-size: 22px;
    box-shadow: 0 4px 20px rgba(200,146,75,0.3);
  }
  .btn.upload { cursor: pointer; }
</style>
