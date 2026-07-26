<script>
  import { onMount } from "svelte";

  // ─── MOCK DATA (replace with API) ───
  let partnerName = "César Holguín";
  let partnerTier = "Socio Fundador";
  let commissionRate = 0.10; // 10% SDC hidden commission
  let activeClients = 12;
  let monthlyRevenue = 46750; // $ USD what partner sees

  // These prices are what the partner SETS for their clients
  // Real costs are NEVER shown
  let prices = {
    inbound_call: { label: "Llamada entrante", price: 3.00, unit: "por llamada", realCost: 0.15 },
    outbound_call: { label: "Llamada saliente", price: 5.00, unit: "por llamada", realCost: 0.15 },
    chat_message: { label: "Chat mensaje", price: 0.25, unit: "por mensaje", realCost: 0.002 },
    image_gen: { label: "Imagen generada", price: 1.00, unit: "por imagen", realCost: 0.05 },
    video_gen: { label: "Video generado", price: 5.00, unit: "por video", realCost: 0.10 },
    agent_hour: { label: "Hora de agente", price: 15.00, unit: "por hora", realCost: 0.50 },
  };

  let recentTransactions = [
    { client: "Maquinados Norte", action: "Llamada entrante", price: 3.00, time: "hace 2 min" },
    { client: "Clínica Dental Hermosillo", action: "Chat mensaje", price: 0.25, time: "hace 8 min" },
    { client: "Despacho Contable Torres", action: "Llamada saliente", price: 5.00, time: "hace 15 min" },
    { client: "Constructora Sonora", action: "Imagen generada", price: 1.00, time: "hace 30 min" },
    { client: "Maquinados Norte", action: "Hora de agente", price: 15.00, time: "hace 45 min" },
  ];

  let editingPrice = null;
  let showRealCosts = false; // ← ESTO NUNCA SE ACTIVA EN PRODUCCIÓN

  // WHAT THE PARTNER SEES (no real costs)
  let partnerEarnings = $derived.by(() => {
    let gross = recentTransactions.reduce((sum, t) => sum + t.price, 0);
    let sdcCommission = gross * commissionRate;
    return gross - sdcCommission;
  });

  onMount(() => {
    // Fetch real data from API when available
  });

  function editPrice(key) { editingPrice = key; }
  function savePrice(key) { editingPrice = null; }
</script>

<div class="dashboard">
  <!-- Header -->
  <div class="header">
    <div class="partner-info">
      <div class="partner-avatar">{partnerName.split(" ").map(n => n[0]).join("")}</div>
      <div>
        <h2>{partnerName}</h2>
        <div class="partner-tier">{partnerTier}</div>
      </div>
    </div>
    <div class="header-stats">
      <div class="stat">
        <div class="stat-value" style="color: #10b981">${monthlyRevenue.toLocaleString()}</div>
        <div class="stat-label">Ganancia este mes</div>
      </div>
      <div class="stat">
        <div class="stat-value">{activeClients}</div>
        <div class="stat-label">Clientes activos</div>
      </div>
      <div class="stat">
        <div class="stat-value">{commissionRate * 100}%</div>
        <div class="stat-label">Comisión SDC</div>
      </div>
    </div>
  </div>

  <!-- Prices Configuration -->
  <div class="section">
    <h3>💰 Tus Precios</h3>
    <p class="section-note">Tú pones el precio. Tus clientes pagan esto. Nosotros nos encargamos del resto.</p>
    
    <div class="prices-grid">
      {#each Object.entries(prices) as [key, item]}
        <div class="price-card">
          <div class="price-label">{item.label}</div>
          <div class="price-control">
            {#if editingPrice === key}
              <input type="number" step="0.25" bind:value={item.price} class="price-input" />
              <button class="save-btn" on:click={() => savePrice(key)}>✓</button>
            {:else}
              <span class="price-value">${item.price.toFixed(2)}</span>
              <button class="edit-btn" on:click={() => editPrice(key)}>✎</button>
            {/if}
          </div>
          <div class="price-unit">{item.unit}</div>
          <!-- ⛔ NUNCA MOSTRAR: costo real SDC -->
        </div>
      {/each}
    </div>
  </div>

  <!-- Earnings Summary (WHAT PARTNER SEES) -->
  <div class="section">
    <h3>📊 Tu Ganancia</h3>
    <div class="earnings-grid">
      <div class="earning-card highlight">
        <div class="earn-label">Ingreso bruto</div>
        <div class="earn-value">${recentTransactions.reduce((s,t) => s + t.price, 0).toFixed(2)}</div>
        <div class="earn-sub">Cobrado a tus clientes</div>
      </div>
      <div class="earning-card">
        <div class="earn-label">Comisión de plataforma</div>
        <div class="earn-value" style="color:#ef4444">-${(recentTransactions.reduce((s,t) => s + t.price, 0) * commissionRate).toFixed(2)}</div>
        <div class="earn-sub">{commissionRate * 100}% · infraestructura + agentes IA</div>
      </div>
      <div class="earning-card highlight">
        <div class="earn-label">TU GANANCIA NETA</div>
        <div class="earn-value" style="color:#10b981">${partnerEarnings.toFixed(2)}</div>
        <div class="earn-sub">Transferencia mensual automática</div>
      </div>
    </div>
    <!-- ⛔ OCULTAR SIEMPRE:
      <p>Costo real SDC: $0.47</p>
      <p>Margen SDC: 94%</p>
    -->
  </div>

  <!-- Recent Activity -->
  <div class="section">
    <h3>🕐 Actividad Reciente</h3>
    <div class="activity-list">
      {#each recentTransactions as tx}
        <div class="activity-item">
          <div class="activity-info">
            <div class="activity-client">{tx.client}</div>
            <div class="activity-action">{tx.action}</div>
          </div>
          <div class="activity-price">${tx.price.toFixed(2)}</div>
          <div class="activity-time">{tx.time}</div>
        </div>
      {/each}
    </div>
  </div>

  <!-- Footer -->
  <div class="footer-note">
    <p>✦ Los costos de infraestructura, modelos de IA y soporte están cubiertos por SDC.</p>
    <p>Tú solo recibes tu ganancia. Sin sorpresas. Sin costos ocultos.</p>
    <p class="legal">SDC recibe una comisión por uso de plataforma. Términos y condiciones disponibles.</p>
  </div>
</div>

<style>
  .dashboard {
    padding: 24px;
    max-width: 1000px;
    margin: 0 auto;
    color: #edf0f7;
    font-family: 'Inter', system-ui, sans-serif;
  }

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
    padding: 24px;
    background: rgba(17,19,30,0.6);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
  }
  .partner-info { display: flex; align-items: center; gap: 16px; }
  .partner-avatar {
    width: 52px; height: 52px; border-radius: 50%;
    background: linear-gradient(135deg, #00d4ff, #7b2fff);
    display: flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 18px; color: #fff;
  }
  .partner-info h2 { font-size: 20px; font-weight: 600; }
  .partner-tier { font-size: 12px; color: #00d4ff; letter-spacing: 1px; text-transform: uppercase; }
  .header-stats { display: flex; gap: 24px; }
  .stat { text-align: center; }
  .stat-value { font-size: 24px; font-weight: 700; }
  .stat-label { font-size: 11px; color: rgba(255,255,255,0.4); text-transform: uppercase; letter-spacing: 1px; margin-top: 2px; }

  .section { margin-bottom: 28px; }
  .section h3 { font-size: 14px; font-weight: 600; margin-bottom: 4px; letter-spacing: 0.5px; }
  .section-note { font-size: 12px; color: rgba(255,255,255,0.3); margin-bottom: 16px; }

  .prices-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
  .price-card {
    padding: 16px; border-radius: 10px;
    background: rgba(17,19,30,0.4); border: 1px solid rgba(255,255,255,0.04);
  }
  .price-label { font-size: 12px; color: rgba(255,255,255,0.5); margin-bottom: 8px; }
  .price-control { display: flex; align-items: center; gap: 8px; }
  .price-value { font-size: 24px; font-weight: 700; color: #00d4ff; }
  .price-input {
    width: 80px; padding: 6px 10px; border-radius: 6px;
    border: 1px solid rgba(0,212,255,0.3); background: rgba(0,0,0,0.3);
    color: #fff; font-size: 18px; font-weight: 700; font-family: inherit;
  }
  .edit-btn, .save-btn {
    background: none; border: none; color: rgba(255,255,255,0.2);
    cursor: pointer; font-size: 16px; padding: 4px;
  }
  .edit-btn:hover { color: rgba(255,255,255,0.6); }
  .save-btn { color: #00d4ff; }
  .price-unit { font-size: 11px; color: rgba(255,255,255,0.2); margin-top: 4px; }

  .earnings-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .earning-card {
    padding: 20px; border-radius: 12px;
    background: rgba(17,19,30,0.4); border: 1px solid rgba(255,255,255,0.04);
  }
  .earning-card.highlight { border-color: rgba(16,185,129,0.15); }
  .earn-label { font-size: 11px; text-transform: uppercase; letter-spacing: 1px; color: rgba(255,255,255,0.4); margin-bottom: 8px; }
  .earn-value { font-size: 28px; font-weight: 700; }
  .earn-sub { font-size: 11px; color: rgba(255,255,255,0.2); margin-top: 4px; }

  .activity-list { display: flex; flex-direction: column; gap: 4px; }
  .activity-item {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px; border-radius: 8px;
    background: rgba(17,19,30,0.2);
  }
  .activity-client { font-size: 13px; font-weight: 500; }
  .activity-action { font-size: 11px; color: rgba(255,255,255,0.3); }
  .activity-price { font-size: 16px; font-weight: 600; color: #10b981; }
  .activity-time { font-size: 11px; color: rgba(255,255,255,0.2); }

  .footer-note { margin-top: 32px; padding: 16px; border-radius: 8px; background: rgba(255,255,255,0.02); }
  .footer-note p { font-size: 11px; color: rgba(255,255,255,0.2); margin: 2px 0; }
  .legal { font-size: 9px; color: rgba(255,255,255,0.1); margin-top: 8px; }
</style>
