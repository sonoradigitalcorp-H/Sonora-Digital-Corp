<script>
  import { onMount } from "svelte";

  let showPage = "pitch";
  let step = 0;
  
  const STEPS = [
    { icon:"🔮", title:"Wake Word", desc:"César dice 'Hey Jarvis' → sistema despierta", cost:"$0", local:true },
    { icon:"🎤", title:"Escucha", desc:"STT con Whisper → texto plano", cost:"$0", local:true },
    { icon:"🧠", title:"Router Cuántico", desc:"80% local, 20% cloud. Decide automáticamente", cost:"$0 → $0.00026", local:true },
    { icon:"🌐", title:"Browser Action", desc:"Playwright navega, extrae, analiza", cost:"$0.00026", local:false },
    { icon:"🔊", title:"Kokoro TTS", desc:"Responde con voz natural española", cost:"$0", local:true },
    { icon:"💰", title:"Costo total", desc:"Interacción completa", cost:"$0.00026 (0.000026¢)", local:false },
  ];

  const PLANS = [
    { name:"Básico", price:"$19", clients:"1-3", margin:"91%", color:"#a8b589" },
    { name:"Pro", price:"$49", clients:"5-10", margin:"94%", color:"#C8924B" },
    { name:"Enterprise", price:"$99", clients:"ilimitados", margin:"96%", color:"#00d4ff" },
  ];

  let audioCtx = null;
  let audioInterval;

  onMount(() => {
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    return () => { if (audioInterval) clearInterval(audioInterval); };
  });

  function playPing(freq = 440) {
    if (!audioCtx) return;
    const osc = audioCtx.createOscillator();
    const gain = audioCtx.createGain();
    osc.connect(gain);
    gain.connect(audioCtx.destination);
    osc.frequency.value = freq;
    gain.gain.setValueAtTime(0.05, audioCtx.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
    osc.start();
    osc.stop(audioCtx.currentTime + 0.3);
  }

  function nextPage(page) { 
    showPage = page; 
    playPing(660);
  }
</script>

<div class="demo-cesar">
  <!-- Header AztroTech -->
  <div class="header">
    <div class="brand">
      <span class="brand-dot"></span>
      <div>
        <h1>AztroTech <span class="light">AI</span></h1>
        <p class="sub">Powered by Sonora Digital Corp · Mystic Grimoire</p>
      </div>
    </div>
    <div class="nav">
      <button class="nav-btn" class:active={showPage==="pitch"} on:click={() => nextPage("pitch")}>📊 Pitch</button>
      <button class="nav-btn" class:active={showPage==="funnel"} on:click={() => nextPage("funnel")}>🧪 Funnel</button>
      <button class="nav-btn" class:active={showPage==="costos"} on:click={() => nextPage("costos")}>💰 Costos</button>
      <button class="nav-btn" class:active={showPage==="plan"} on:click={() => nextPage("plan")}>🎯 Plan</button>
    </div>
  </div>

  <div class="content">
    {#if showPage === "pitch"}
    <!-- PÁGINA 1: PITCH -->
    <div class="pitch-page">
      <div class="hero">
        <div class="hero-icon">✦</div>
        <h2>Tu Propio ChatGPT <span class="highlight">Blanco y Negro</span></h2>
        <p class="hero-sub">Con tu logo. Tu personalidad. Tu negocio. Sin servidores. Sin código. Sin dolores de cabeza.</p>
      </div>

      <div class="features">
        <div class="feature-card" on:click={() => playPing(880)}>
          <span class="f-icon">🎙️</span>
          <h3>Voz Natural</h3>
          <p>Kokoro TTS habla como tú. Tus clientes creen que eres tú.</p>
          <span class="tag">LOCAL · $0</span>
        </div>
        <div class="feature-card" on:click={() => playPing(880)}>
          <span class="f-icon">🤖</span>
          <h3>Agente Autónomo</h3>
          <p>CRM, calendario, ventas, soporte. Todo en uno. Todo automático.</p>
          <span class="tag">24/7 · SIN MANOS</span>
        </div>
        <div class="feature-card" on:click={() => playPing(880)}>
          <span class="f-icon">📊</span>
          <h3>Dashboard 3D</h3>
          <p>Ves tu negocio en tiempo real. Cada cliente, cada costo, cada acción.</p>
          <span class="tag">GRIMOIRE · ∞</span>
        </div>
        <div class="feature-card" on:click={() => playPing(880)}>
          <span class="f-icon">💸</span>
          <h3>Margen 94%</h3>
          <p>Cada cliente te cuesta $1.69. Lo vendes en $29. La cuenta la haces tú.</p>
          <span class="tag">NEGOCIO REAL</span>
        </div>
      </div>

      <div class="cta-section">
        <button class="cta-btn" on:click={() => nextPage("funnel")}>Ver cómo funciona →</button>
      </div>
    </div>

    {:else if showPage === "funnel"}
    <!-- PÁGINA 2: FUNNEL CUÁNTICO -->
    <div class="funnel-page">
      <h2>🧪 El Funnel Cuántico</h2>
      <p class="funnel-intro">Cada interacción es una partícula que viaja por el sistema. Así funciona:</p>

      <div class="funnel-steps">
        {#each STEPS as s, i}
        <div class="funnel-step" class:active={step === i} on:click={() => { step = i; playPing(440 + i * 80); }}>
          <div class="step-num">{i + 1}</div>
          <div class="step-content">
            <div class="step-header">
              <span class="step-icon">{s.icon}</span>
              <strong>{s.title}</strong>
              <span class="step-cost" class:free={s.local}>{s.cost}</span>
            </div>
            <p>{s.desc}</p>
            {#if s.local}
              <div class="step-local">⚡ PROCESAMIENTO LOCAL · 0 EMISIONES</div>
            {:else}
              <div class="step-cloud">☁️ PROCESAMIENTO CLOUD · ${s.cost.replace("$", "")}</div>
            {/if}
          </div>
        </div>
        {/each}
      </div>

      <div class="funnel-total">
        <div class="total-cost">$0.00026</div>
        <div class="total-label">COSTO TOTAL POR INTERACCIÓN</div>
        <div class="total-compare">
          Competencia: $0.01 - $0.05 · <strong>SDC: 60x más barato</strong>
        </div>
      </div>
    </div>

    {:else if showPage === "costos"}
    <!-- PÁGINA 3: COSTOS -->
    <div class="costos-page">
      <h2>💰 Matriz de Costos Cuánticos</h2>
      <p class="costos-sub">80% de las operaciones son GRATIS (local). Solo pagas cuando el sistema piensa en serio.</p>

      <div class="cost-grid">
        <div class="cost-card free">
          <div class="cost-header">
            <span class="cost-icon">💻</span>
            <h3>LOCAL · $0</h3>
          </div>
          <ul>
            <li>🔮 Wake word detection</li>
            <li>🎙️ Transcripción (Whisper)</li>
            <li>🔊 Síntesis de voz (Kokoro)</li>
            <li>🏷️ Clasificar intención</li>
            <li>💬 Chat simple</li>
            <li>📊 Embeddings RAG</li>
          </ul>
          <div class="cost-pct">80% de las operaciones</div>
        </div>

        <div class="cost-card cloud">
          <div class="cost-header">
            <span class="cost-icon">☁️</span>
            <h3>CLOUD · $0.00026</h3>
          </div>
          <ul>
            <li>🌐 Browser actions</li>
            <li>🧠 Razonamiento complejo</li>
            <li>📈 Análisis de costos</li>
            <li>🔍 Búsqueda web</li>
            <li>🧬 Memoria RAG</li>
            <li>✍️ Generación contenido</li>
          </ul>
          <div class="cost-pct">20% de las operaciones</div>
        </div>
      </div>

      <div class="cost-summary">
        <div class="summary-item">
          <span class="s-value">$16.88</span>
          <span class="s-label">Costo fijo mensual</span>
        </div>
        <div class="summary-item">
          <span class="s-value">$1.69</span>
          <span class="s-label">Costo por cliente/mes</span>
        </div>
        <div class="summary-item">
          <span class="s-value">94%</span>
          <span class="s-label">Margen vendiendo a $29</span>
        </div>
      </div>
    </div>

    {:else if showPage === "plan"}
    <!-- PÁGINA 4: PLAN DE ACCIÓN -->
    <div class="plan-page">
      <h2>🎯 Lunes con César — El Plan</h2>
      
      <div class="timeline">
        <div class="tl-item">
          <div class="tl-time">9:00</div>
          <div class="tl-content">
            <strong>📊 Demo del Grimoire</strong>
            <p>Le enseñas el ∞ 3D con su marca AztroTech. Le dices: "Esto es tuyo. Así ves tu negocio."</p>
          </div>
        </div>
        <div class="tl-item">
          <div class="tl-time">9:15</div>
          <div class="tl-content">
            <strong>🎤 Prueba de Voz</strong>
            <p>Le dices "Di algo" → Kokoro le responde con su voz. Se sorprende.</p>
          </div>
        </div>
        <div class="tl-item">
          <div class="tl-time">9:25</div>
          <div class="tl-content">
            <strong>💰 La Matemática</strong>
            <p>1 cliente = $1.69 costo. Lo vende en $29. 10 clientes = $273 ganancia mensual.</p>
          </div>
        </div>
        <div class="tl-item">
          <div class="tl-time">9:35</div>
          <div class="tl-content">
            <strong>🤝 Cierre</strong>
            <p>"¿Con cuántos clientes quieres empezar? ¿3, 5, 10? En 5 minutos tienes su agente listo."</p>
          </div>
        </div>
      </div>

      <div class="pricing-plans">
        {#each PLANS as plan}
        <div class="plan-card" style="border-color: {plan.color}" on:click={() => playPing(880)}>
          <div class="plan-name">{plan.name}</div>
          <div class="plan-price">{plan.price}<span class="plan-period">/mes</span></div>
          <div class="plan-clients">Hasta {plan.clients} clientes</div>
          <div class="plan-margin" style="color: {plan.color}">Margen {plan.margin}</div>
          <button class="plan-btn" style="background: {plan.color}">Comenzar</button>
        </div>
        {/each}
      </div>
    </div>
    {/if}
  </div>

  <div class="footer">
    <span>✦ Mystic Grimoire · Sonora Digital Corp</span>
    <span class="footer-cost">Costo esta demo: $0.00000 (100% local)</span>
  </div>
</div>

<style>
  .demo-cesar {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    background: linear-gradient(135deg, #08090f 0%, #0a0e1a 100%);
    overflow: hidden;
  }

  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 24px;
    border-bottom: 1px solid rgba(0,212,255,0.08);
    background: rgba(0,0,0,0.3);
  }
  .brand { display: flex; align-items: center; gap: 12px; }
  .brand-dot { 
    width: 10px; height: 10px; border-radius: 50%;
    background: #00d4ff; box-shadow: 0 0 16px #00d4ff;
  }
  .brand h1 { font-size: 16px; font-weight: 700; color: #fff; letter-spacing: 1px; }
  .brand .light { font-weight: 300; color: #00d4ff; }
  .sub { font-size: 10px; color: rgba(255,255,255,0.3); letter-spacing: 1px; margin-top: 1px; }

  .nav { display: flex; gap: 4px; }
  .nav-btn {
    padding: 6px 14px; border-radius: 6px; border: 1px solid transparent;
    background: transparent; color: rgba(255,255,255,0.4); font-size: 11px;
    cursor: pointer; transition: 0.2s; font-family: inherit;
  }
  .nav-btn:hover { border-color: rgba(0,212,255,0.2); color: #fff; }
  .nav-btn.active { background: rgba(0,212,255,0.1); border-color: rgba(0,212,255,0.3); color: #00d4ff; }

  .content { flex: 1; overflow-y: auto; padding: 24px; }

  /* Pitch Page */
  .hero { text-align: center; margin-bottom: 32px; }
  .hero-icon { 
    font-size: 48px; margin-bottom: 8px; display: inline-block;
    animation: spin 4s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .hero h2 { font-size: 28px; font-weight: 300; color: #fff; margin-bottom: 8px; }
  .highlight { color: #00d4ff; font-weight: 700; }
  .hero-sub { font-size: 14px; color: rgba(255,255,255,0.4); max-width: 500px; margin: 0 auto; }

  .features { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 24px; }
  .feature-card {
    padding: 20px; border-radius: 12px;
    border: 1px solid rgba(0,212,255,0.06);
    background: rgba(0,212,255,0.02);
    cursor: pointer; transition: 0.3s;
  }
  .feature-card:hover { border-color: rgba(0,212,255,0.2); background: rgba(0,212,255,0.04); }
  .f-icon { font-size: 32px; margin-bottom: 8px; display: block; }
  .feature-card h3 { font-size: 15px; margin-bottom: 6px; color: #fff; }
  .feature-card p { font-size: 12px; color: rgba(255,255,255,0.4); line-height: 1.5; }
  .tag {
    display: inline-block; margin-top: 8px; padding: 3px 10px;
    border-radius: 10px; font-size: 9px; letter-spacing: 1px;
    background: rgba(0,212,255,0.08); color: #00d4ff; border: 1px solid rgba(0,212,255,0.15);
  }

  .cta-section { text-align: center; }
  .cta-btn {
    padding: 14px 32px; border-radius: 30px; border: none;
    background: linear-gradient(135deg, #00d4ff, #7b2fff);
    color: #fff; font-size: 15px; font-weight: 600; cursor: pointer;
    font-family: inherit; transition: 0.3s;
  }
  .cta-btn:hover { transform: scale(1.03); box-shadow: 0 0 30px rgba(0,212,255,0.3); }

  /* Funnel */
  .funnel-page h2, .costos-page h2, .plan-page h2 {
    font-size: 22px; font-weight: 300; color: #fff; margin-bottom: 8px;
  }
  .funnel-intro, .costos-sub { font-size: 13px; color: rgba(255,255,255,0.4); margin-bottom: 20px; }

  .funnel-steps { display: flex; flex-direction: column; gap: 8px; margin-bottom: 24px; }
  .funnel-step {
    display: flex; gap: 12px; padding: 14px; border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.04); background: rgba(255,255,255,0.02);
    cursor: pointer; transition: 0.3s;
  }
  .funnel-step:hover, .funnel-step.active { border-color: rgba(0,212,255,0.2); background: rgba(0,212,255,0.04); }
  .step-num {
    width: 28px; height: 28px; border-radius: 50%;
    background: rgba(0,212,255,0.1); color: #00d4ff;
    display: flex; align-items: center; justify-content: center;
    font-size: 12px; font-weight: 700; flex-shrink: 0;
  }
  .step-content { flex: 1; }
  .step-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }
  .step-header strong { font-size: 13px; color: #fff; }
  .step-cost { 
    margin-left: auto; font-size: 11px; padding: 2px 8px; border-radius: 8px;
    background: rgba(0,212,255,0.1); color: #00d4ff;
  }
  .step-cost.free { background: rgba(168,181,137,0.1); color: #a8b589; }
  .step-content p { font-size: 12px; color: rgba(255,255,255,0.4); }
  .step-local { font-size: 10px; color: #a8b589; margin-top: 4px; letter-spacing: 1px; }
  .step-cloud { font-size: 10px; color: #00d4ff; margin-top: 4px; letter-spacing: 1px; }

  .funnel-total { text-align: center; padding: 20px; background: rgba(0,212,255,0.03); border-radius: 12px; border: 1px solid rgba(0,212,255,0.1); }
  .total-cost { font-size: 36px; font-weight: 200; color: #00d4ff; }
  .total-label { font-size: 11px; color: rgba(255,255,255,0.3); letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }
  .total-compare { font-size: 11px; color: rgba(255,255,255,0.3); margin-top: 8px; }

  /* Costos */
  .cost-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 24px; }
  .cost-card {
    padding: 20px; border-radius: 12px;
    background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.06);
  }
  .cost-card.free { border-color: rgba(168,181,137,0.15); }
  .cost-card.cloud { border-color: rgba(0,212,255,0.15); }
  .cost-header { display: flex; align-items: center; gap: 8px; margin-bottom: 12px; }
  .cost-icon { font-size: 20px; }
  .cost-header h3 { font-size: 14px; color: #fff; }
  .cost-card ul { list-style: none; padding: 0; }
  .cost-card li { font-size: 12px; color: rgba(255,255,255,0.5); padding: 4px 0; }
  .cost-pct {
    margin-top: 12px; font-size: 20px; font-weight: 300;
    padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.06);
  }
  .cost-card.free .cost-pct { color: #a8b589; }
  .cost-card.cloud .cost-pct { color: #00d4ff; }

  .cost-summary { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .summary-item { text-align: center; padding: 16px; border-radius: 10px; background: rgba(255,255,255,0.02); border: 1px solid rgba(255,255,255,0.04); }
  .s-value { font-size: 28px; font-weight: 300; color: #00d4ff; display: block; }
  .s-label { font-size: 11px; color: rgba(255,255,255,0.3); margin-top: 4px; }

  /* Plan */
  .timeline { display: flex; flex-direction: column; gap: 12px; margin-bottom: 24px; }
  .tl-item { display: flex; gap: 16px; }
  .tl-time { 
    width: 50px; font-size: 12px; font-weight: 700; color: #00d4ff;
    text-align: right; flex-shrink: 0;
  }
  .tl-content { 
    padding: 12px 16px; border-radius: 8px;
    border-left: 2px solid rgba(0,212,255,0.15);
    background: rgba(0,212,255,0.02);
  }
  .tl-content strong { font-size: 13px; color: #fff; display: block; margin-bottom: 4px; }
  .tl-content p { font-size: 12px; color: rgba(255,255,255,0.4); margin: 0; }

  .pricing-plans { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .plan-card {
    text-align: center; padding: 20px; border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.06); background: rgba(255,255,255,0.02);
    cursor: pointer; transition: 0.3s;
  }
  .plan-card:hover { transform: translateY(-4px); }
  .plan-name { font-size: 13px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
  .plan-price { font-size: 32px; font-weight: 300; color: #fff; }
  .plan-period { font-size: 14px; color: rgba(255,255,255,0.3); }
  .plan-clients { font-size: 12px; color: rgba(255,255,255,0.3); margin: 8px 0; }
  .plan-margin { font-size: 14px; font-weight: 700; margin-bottom: 12px; }
  .plan-btn {
    padding: 8px 24px; border-radius: 20px; border: none;
    color: #fff; font-size: 12px; cursor: pointer; font-family: inherit;
    transition: 0.3s;
  }
  .plan-btn:hover { transform: scale(1.05); }

  .footer {
    padding: 8px 24px; border-top: 1px solid rgba(255,255,255,0.04);
    display: flex; justify-content: space-between;
    font-size: 10px; color: rgba(255,255,255,0.15); letter-spacing: 1px;
  }
  .footer-cost { color: #a8b589; }

  @media(max-width: 768px) {
    .features { grid-template-columns: 1fr; }
    .cost-grid { grid-template-columns: 1fr; }
    .pricing-plans { grid-template-columns: 1fr; }
    .nav { flex-wrap: wrap; }
    .header { flex-direction: column; gap: 8px; }
  }
</style>
