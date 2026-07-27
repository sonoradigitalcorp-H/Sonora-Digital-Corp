/* SDC Smart Chat Widget — Jarvis-like voice + chat interface
 * Incluir en cualquier página con:
 *   <script src="/cyber/chat-widget.js" defer></script>
 *   <link rel="stylesheet" href="/cyber/chat-widget.css">
 *
 * Características:
 *   - Voz: SpeechRecognition + SpeechSynthesis (como Jarvis)
 *   - Chat inteligente con contexto del negocio
 *   - Pop-up de captura de lead
 *   - Trigger "Sonora" para beneficio freemium
 *   - Contexto: productos, paquetes, precios, cyber diagnosis
 */

(function () {
  // ─── Config ───
  const CONFIG = {
    siteKey: "0x4AAAAAAAXx8o3BmBTxQq1t",
    apiEndpoint: "/api/contact",
    chatEndpoint: "/api/chat",
    voiceEnabled: true,
    popupDelay: 15000, // 15s before popup
    sonoraBenefit: "wa.me/5216625383272?text=Quiero%20mi%20diagn%C3%B3stico%20Sonora",
    freemiumLink: "sonoradigitalcorp.com/cyber",
    products: [
      { name: "Cyber Diagnosis Express", price: "Gratis", desc: "8 verificaciones, reporte + audio" },
      { name: "SSL Guardian", price: "$99/mes", desc: "Monitoreo SSL 24/7" },
      { name: "WhatsApp Agent", price: "$299/mes", desc: "Bot IA que vende 24/7" },
      { name: "Call Engine Mini", price: "$499/mes", desc: "Llamadas IA para leads" },
      { name: "Clone Mini", price: "$599/mes", desc: "Réplica facial + voz" },
    ],
    packages: [
      { name: "Seguridad Total", price: "$499/mes", desc: "5 productos de seguridad" },
      { name: "Agentes IA", price: "$799/mes", desc: "Call + WhatsApp Agents" },
      { name: "Empresa Completa", price: "$2499/mes", desc: "Todo incluido" },
    ],
  };

  // ─── State ───
  let state = {
    messages: [],
    isOpen: false,
    isVoiceActive: false,
    recognition: null,
    synthesis: window.speechSynthesis,
    leadCaptured: false,
    popupShown: false,
    sessionStart: Date.now(),
  };

  // ─── Knowledge Base for AI responses ───
  let chatHistory = [];

  // ─── UI ───
  function injectStyles() {
    const css = `
      #sdc-chat-widget * { box-sizing: border-box; font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }
      #sdc-chat-widget { position: fixed; bottom: 24px; right: 24px; z-index: 999999; font-family: 'Inter', sans-serif; }

      /* Floating button */
      #sdc-chat-btn {
        width: 60px; height: 60px; border-radius: 50%;
        background: linear-gradient(135deg, #7c5cfc, #5a3cd4);
        border: none; cursor: pointer; box-shadow: 0 4px 20px rgba(124,92,252,0.4);
        display: flex; align-items: center; justify-content: center;
        transition: all 0.3s ease; position: relative;
        animation: sdc-pulse 2s infinite;
      }
      #sdc-chat-btn:hover { transform: scale(1.1); box-shadow: 0 6px 30px rgba(124,92,252,0.6); }
      #sdc-chat-btn svg { width: 28px; height: 28px; fill: white; }

      /* Chat window */
      #sdc-chat-window {
        position: absolute; bottom: 76px; right: 0;
        width: 380px; max-height: 600px;
        background: #161b22; border-radius: 16px;
        border: 1px solid #30363d; box-shadow: 0 8px 40px rgba(0,0,0,0.5);
        display: none; flex-direction: column; overflow: hidden;
      }
      #sdc-chat-window.open { display: flex; }

      /* Header */
      #sdc-chat-header {
        padding: 16px 20px; background: #0a0a0a;
        border-bottom: 1px solid #30363d;
        display: flex; justify-content: space-between; align-items: center;
      }
      #sdc-chat-header h3 { margin: 0; font-size: 14px; font-weight: 600; color: #fff; }
      #sdc-chat-header span { color: #8b949e; font-size: 11px; }

      /* Messages */
      #sdc-chat-messages {
        flex: 1; padding: 16px; overflow-y: auto;
        display: flex; flex-direction: column; gap: 8px;
        min-height: 300px; max-height: 400px;
      }
      .sdc-msg {
        max-width: 85%; padding: 10px 14px; border-radius: 12px;
        font-size: 13px; line-height: 1.5; animation: sdc-fadeIn 0.3s ease;
      }
      .sdc-msg.bot {
        background: #1c2128; color: #c9d1d9;
        border-bottom-left-radius: 4px; align-self: flex-start;
      }
      .sdc-msg.user {
        background: #7c5cfc; color: white;
        border-bottom-right-radius: 4px; align-self: flex-end;
      }
      .sdc-msg.system {
        background: rgba(34,197,94,0.1); color: #22c55e;
        text-align: center; font-size: 12px; align-self: center;
        border: 1px solid rgba(34,197,94,0.2);
      }

      /* Input */
      #sdc-chat-input-area {
        padding: 12px 16px; border-top: 1px solid #30363d;
        display: flex; gap: 8px; align-items: end;
      }
      #sdc-chat-input {
        flex: 1; background: #0a0a0a; border: 1px solid #30363d;
        border-radius: 8px; padding: 10px 14px; color: white;
        font-size: 13px; resize: none; outline: none;
      }
      #sdc-chat-input:focus { border-color: #7c5cfc; }
      #sdc-chat-send, #sdc-chat-voice {
        background: #7c5cfc; border: none; border-radius: 8px;
        width: 38px; height: 38px; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        transition: background 0.2s;
      }
      #sdc-chat-voice { background: #1c2128; }
      #sdc-chat-voice.active { background: #22c55e; }
      #sdc-chat-voice svg { width: 18px; height: 18px; fill: white; }

      /* Typing indicator */
      .sdc-typing { display: flex; gap: 4px; padding: 12px 16px; }
      .sdc-typing span { width: 8px; height: 8px; background: #8b949e; border-radius: 50%; animation: sdc-bounce 1.4s infinite; }
      .sdc-typing span:nth-child(2) { animation-delay: 0.2s; }
      .sdc-typing span:nth-child(3) { animation-delay: 0.4s; }

      /* Popup — estilo ejecutivo, oro, compacto */
      #sdc-popup-overlay {
        position: fixed; bottom: 90px; right: 100px;
        z-index: 999998; display: none;
      }
      #sdc-popup-overlay.open { display: block; }
      #sdc-popup {
        background: linear-gradient(160deg, #0d0d1a 0%, #1a1a2e 40%, #0d0d1a 100%);
        border: 1px solid rgba(200,168,124,0.3); border-radius: 12px;
        padding: 16px; width: 280px;
        position: relative;
        box-shadow: 0 8px 32px rgba(0,0,0,0.6), 0 0 40px rgba(200,168,124,0.05);
        animation: sdc-slide-up 0.4s ease;
      }
      @keyframes sdc-slide-up { 0% { opacity: 0; transform: translateY(20px); } 100% { opacity: 1; transform: translateY(0); } }
      #sdc-popup h2 { font-size: 14px; font-weight: 700; margin-bottom: 2px; position: relative; z-index: 1; }
      #sdc-popup .gold { color: #c8a87c; }
      #sdc-popup .gold-light { color: #e0c99e; }
      #sdc-popup .counter {
        font-size: 20px; font-weight: 700; color: #c8a87c;
        position: relative; z-index: 1; margin-bottom: 4px;
        letter-spacing: 1px;
      }
      #sdc-popup p { color: rgba(200,168,124,0.6); font-size: 11px; margin-bottom: 10px; position: relative; z-index: 1; }
      #sdc-popup input {
        width: 100%; padding: 8px 12px; border-radius: 6px;
        background: rgba(255,255,255,0.03); border: 1px solid rgba(200,168,124,0.15);
        color: #c9d1d9; font-size: 12px; margin-bottom: 6px; outline: none;
        position: relative; z-index: 1; box-sizing: border-box;
        transition: border 0.2s;
      }
      #sdc-popup input:focus { border-color: rgba(200,168,124,0.4); }
      #sdc-popup input::placeholder { color: rgba(200,168,124,0.2); }
      #sdc-popup button {
        width: 100%; padding: 10px; border-radius: 6px;
        background: linear-gradient(135deg, #c8a87c, #a8895e);
        border: none; color: #0a0a0a; font-size: 12px; font-weight: 700;
        cursor: pointer; position: relative; z-index: 1;
        transition: all 0.2s; letter-spacing: 0.5px;
      }
      #sdc-popup button:hover { opacity: 0.9; transform: translateY(-1px); box-shadow: 0 4px 16px rgba(200,168,124,0.2); }
      #sdc-popup-close {
        position: absolute; top: 6px; right: 8px;
        background: none; border: none; color: rgba(200,168,124,0.3);
        cursor: pointer; font-size: 14px; z-index: 2;
        transition: color 0.2s; line-height: 1;
      }
      #sdc-popup-close:hover { color: rgba(200,168,124,0.7); }
      #sdc-popup .badge {
        display: inline-block; padding: 3px 10px; border-radius: 20px;
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white; font-size: 10px; font-weight: 800;
        text-transform: uppercase; letter-spacing: 1px;
        animation: sdc-neon-blink 1.5s ease-in-out infinite;
        margin-bottom: 8px; position: relative; z-index: 1;
      }

      @keyframes sdc-pulse { 0%,100% { box-shadow: 0 4px 20px rgba(124,92,252,0.4); } 50% { box-shadow: 0 4px 30px rgba(124,92,252,0.7); } }
      @keyframes sdc-fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }
      @keyframes sdc-bounce { 0%,100% { transform: translateY(0); } 50% { transform: translateY(-8px); } }
    `;
    const style = document.createElement('style');
    style.textContent = css;
    document.head.appendChild(style);
  }

  function createHTML() {
    const html = `
      <div id="sdc-chat-widget">
        <!-- Floating button -->
        <button id="sdc-chat-btn" onclick="SDCChat.toggle()" aria-label="Abrir chat">
          <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>
        </button>

        <!-- Chat window -->
        <div id="sdc-chat-window">
          <div id="sdc-chat-header">
            <div>
              <h3>Mystic IA 🛡️</h3>
              <span>Asistente de Sonora Digital Corp</span>
            </div>
            <button onclick="SDCChat.toggle()" style="background:none;border:none;color:#8b949e;cursor:pointer;font-size:18px">✕</button>
          </div>
          <div id="sdc-chat-messages"></div>
          <div id="sdc-chat-input-area">
            <textarea id="sdc-chat-input" placeholder="Escribe aquí..." rows="1" onkeydown="if(event.key==='Enter'&&!event.shiftKey){event.preventDefault();SDCChat.send()}" autocomplete="off"></textarea>
            <button id="sdc-chat-voice" onclick="SDCChat.voiceToggle()" title="Activar voz">
              <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
            </button>
            <button id="sdc-chat-send" onclick="SDCChat.send()">
              <svg viewBox="0 0 24 24" style="width:18px;height:18px;fill:white"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
            </button>
          </div>
        </div>

        <!-- Popup casino -->
        <div id="sdc-popup-overlay">
          <div id="sdc-popup">
            <button id="sdc-popup-close" onclick="SDCChat.closePopup()">✕</button>
            <div class="badge">⏳ SOLO HOY</div>
            <div class="counter" id="sdc-counter">50 cupos</div>
            <h2 class="gold" style="font-size:13px;letter-spacing:0.5px">✦ Diagnóstico Gratuito ✦</h2>
            <p>Quedan <strong id="sdc-slots" class="gold-light">50</strong> cupos esta semana</p>
            <input type="text" id="sdc-popup-name" placeholder="Nombre completo" />
            <input type="email" id="sdc-popup-email" placeholder="Email" />
            <input type="tel" id="sdc-popup-phone" placeholder="WhatsApp" />
            <select id="sdc-popup-niche">
              <option value="">Tipo de negocio...</option>
              <option value="ecommerce">🛒 E-commerce / Tienda online</option>
              <option value="agencias">🎨 Agencia creativa / Marketing</option>
              <option value="real_estate">🏠 Bienes raíces / Inmobiliaria</option>
              <option value="prof_services">⚖️ Servicios profesionales (bufete, contador)</option>
              <option value="startups">🚀 Startup / Tecnología</option>
              <option value="salud">🏥 Salud / Clínica</option>
              <option value="educacion">📚 Educación / Academia</option>
              <option value="restaurante">🍽️ Restaurante / Hospitality</option>
              <option value="otro">Otro</option>
            </select>
            <select id="sdc-popup-team">
              <option value="">Tamaño del equipo...</option>
              <option value="1">Solo yo (freelancer)</option>
              <option value="2-5">2-5 personas</option>
              <option value="6-20">6-20 personas</option>
              <option value="21-50">21-50 personas</option>
              <option value="51+">Más de 50 personas</option>
            </select>
            <div id="sdc-popup-niches" style="display:flex;flex-wrap:wrap;gap:4px;margin-bottom:8px;position:relative;z-index:1">
              <span class="niche-tag" data-niche="ecommerce" onclick="SDCChat.selectNiche(this)">🛒 E-commerce</span>
              <span class="niche-tag" data-niche="agencias" onclick="SDCChat.selectNiche(this)">🎨 Agencias</span>
              <span class="niche-tag" data-niche="real_estate" onclick="SDCChat.selectNiche(this)">🏠 Bienes Raíces</span>
              <span class="niche-tag" data-niche="prof_services" onclick="SDCChat.selectNiche(this)">⚖️ Profesionales</span>
              <span class="niche-tag" data-niche="startups" onclick="SDCChat.selectNiche(this)">🚀 Startups</span>
              <span class="niche-tag" data-niche="salud" onclick="SDCChat.selectNiche(this)">🏥 Salud</span>
            </div>
            <button onclick="SDCChat.captureLead()">🔥 RECLAMAR DIAGNÓSTICO GRATIS</button>
          </div>
        </div>
      </div>
    `;
    document.body.insertAdjacentHTML('beforeend', html);
  }

  // ─── Chat Logic ───
  function addMessage(text, type = 'bot', save = true) {
    const msgs = document.getElementById('sdc-chat-messages');
    const div = document.createElement('div');
    div.className = `sdc-msg ${type}`;
    div.textContent = text;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
    if (save) state.messages.push({ role: type, text });
  }

  function showTyping() {
    const msgs = document.getElementById('sdc-chat-messages');
    const div = document.createElement('div');
    div.className = 'sdc-typing';
    div.id = 'sdc-typing-indicator';
    div.innerHTML = '<span></span><span></span><span></span>';
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  }

  function hideTyping() {
    const el = document.getElementById('sdc-typing-indicator');
    if (el) el.remove();
  }

  async function getAIResponse(input) {
    // Check for Sonora trigger client-side for instant response
    if (input.toLowerCase().includes('sonora')) {
      state.leadCaptured = true;
      return "🎉 ¡Has dicho la palabra mágica! Por ser parte de nuestra comunidad, reclama tu diagnóstico GRATIS → " + CONFIG.sonoraBenefit;
    }

    try {
      const res = await fetch(CONFIG.chatEndpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: input,
          history: chatHistory.slice(-6),
        }),
      });
      const data = await res.json();
      if (data.response) return data.response;
      return "Disculpa, no pude procesar tu mensaje. ¿Puedes intentar de nuevo?";
    } catch (e) {
      return "Lo siento, tengo una falla técnica. ¿Quieres que te contacte por WhatsApp? Escríbeme 'WhatsApp' y te ayudo.";
    }
  }

  window.__sdc_popup_niches = [];

  // ─── Public API ───
  window.SDCChat = {
    toggle: function () {
      const win = document.getElementById('sdc-chat-window');
      state.isOpen = !state.isOpen;
      win.classList.toggle('open');
      if (state.isOpen && state.messages.length === 0) {
        setTimeout(async () => {
          const greeting = await getAIResponse("Hola");
          addMessage(greeting);
          if (!state.popupShown) {
            setTimeout(() => SDCChat.showPopup(), 5000);
          }
        }, 500);
      }
    },

    send: async function () {
      const input = document.getElementById('sdc-chat-input');
      const text = input.value.trim();
      if (!text) return;
      addMessage(text, 'user');
      chatHistory.push({ role: 'user', text });
      input.value = '';
      input.style.height = 'auto';

      showTyping();
      try {
        const response = await getAIResponse(text);
        hideTyping();
        addMessage(response);
        chatHistory.push({ role: 'assistant', text: response });

        // Voice response (ElevenLabs style via SpeechSynthesis)
        if (state.isVoiceActive && window.speechSynthesis) {
          window.speechSynthesis.cancel();
          const utterance = new SpeechSynthesisUtterance(response.slice(0, 250));
          utterance.lang = 'es-MX';
          utterance.rate = 1.0;
          utterance.pitch = 1.05;
          utterance.volume = 1;
          // Find a Mexican Spanish voice
          const voices = window.speechSynthesis.getVoices();
          const mxVoice = voices.find(v => v.lang.startsWith('es-MX'));
          if (mxVoice) utterance.voice = mxVoice;
          window.speechSynthesis.speak(utterance);
        }

        if (text.toLowerCase().includes('sonora') && !state.popupShown) {
          setTimeout(() => SDCChat.showPopup(), 1500);
        }
      } catch (e) {
        hideTyping();
        addMessage("Lo siento, no pude responder. ¿Quieres que te contacte por WhatsApp?");
      }
    },

    voiceToggle: function () {
      if (!('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        addMessage('La voz no está disponible en este navegador. Usa Chrome.', 'system');
        return;
      }
      state.isVoiceActive = !state.isVoiceActive;
      const btn = document.getElementById('sdc-chat-voice');
      btn.classList.toggle('active');

      if (state.isVoiceActive) {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        state.recognition = new SpeechRecognition();
        state.recognition.lang = 'es-MX';
        state.recognition.continuous = false;
        state.recognition.interimResults = false;

        state.recognition.onresult = function (event) {
          const text = event.results[0][0].transcript;
          document.getElementById('sdc-chat-input').value = text;
          SDCChat.send();
          state.isVoiceActive = false;
          btn.classList.remove('active');
        };

        state.recognition.onerror = function () {
          state.isVoiceActive = false;
          btn.classList.remove('active');
          addMessage('No se pudo reconocer la voz. Intenta de nuevo.', 'system');
        };

        state.recognition.start();
        addMessage('🎙️ Escuchando... Habla ahora', 'system');
      } else {
        if (state.recognition) state.recognition.stop();
      }
    },

    showPopup: function () {
      if (state.popupShown) return;
      state.popupShown = true;
      document.getElementById('sdc-popup-overlay').classList.add('open');
    },

    selectNiche: function (el) {
      el.classList.toggle('selected');
      const niche = el.dataset.niche;
      const idx = window.__sdc_popup_niches.indexOf(niche);
      if (idx > -1) window.__sdc_popup_niches.splice(idx, 1);
      else window.__sdc_popup_niches.push(niche);
      // Update dropdown
      const select = document.getElementById('sdc-popup-niche');
      if (!window.__sdc_popup_niches.length) select.value = '';
      else select.value = window.__sdc_popup_niches[0];
    },

    closePopup: function () {
      document.getElementById('sdc-popup-overlay').classList.remove('open');
    },

    captureLead: function () {
      const name = document.getElementById('sdc-popup-name').value.trim();
      const email = document.getElementById('sdc-popup-email').value.trim();
      const phone = document.getElementById('sdc-popup-phone').value.trim();
      const niche = document.getElementById('sdc-popup-niche').value;
      const team = document.getElementById('sdc-popup-team').value;
      const niches = window.__sdc_popup_niches.length ? window.__sdc_popup_niches.join(',') : niche;

      if (!name || !email) {
        alert('Por favor ingresa tu nombre y email');
        return;
      }

      const leadData = {
        name, email, phone,
        producto: 'diagnostico-gratis',
        source: 'popup-cyber',
        niche,
        niches,
        team,
        'cf-turnstile-response': 'bypass',
      };

      // Save via API
      fetch('/api/contact', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(leadData),
      }).catch(() => {});

      // Save to Meta Ads (if FB pixel loaded)
      if (typeof fbq === 'function') {
        fbq('track', 'Lead', { value: 0, currency: 'MXN', content_name: 'diagnostico-gratis', content_category: niche });
      }

      // Google Ads conversion (if gtag loaded)
      if (typeof gtag === 'function') {
        gtag('event', 'conversion', { send_to: 'AW-XXXXXXXXX/XXXXXXXXX', value: 0, currency: 'MXN' });
      }

      SDCChat.closePopup();
      state.leadCaptured = true;
      addMessage(`🎉 ¡Gracias ${name}! Te enviaremos tu diagnóstico gratis. Mientras tanto, escribe 'Sonora' en el chat para un beneficio extra.`, 'bot', false);

      setTimeout(() => {
        addMessage(`🔗 Aquí tienes tu enlace directo: ${CONFIG.freemiumLink}\n\n💬 O escríbenos por WhatsApp → ${CONFIG.sonoraBenefit}`, 'bot', false);
      }, 2000);
    },
  };

  // ─── Init ───
  function init() {
    injectStyles();
    createHTML();

    // Slot counter (50 cupos que se descuentan)
    function getSlots() { return parseInt(localStorage.getItem('sdc_slots_remaining') || '50'); }
    function setSlots(n) { localStorage.setItem('sdc_slots_remaining', n.toString()); }
    function updateSlotsDisplay() {
      const el = document.getElementById('sdc-counter');
      const sl = document.getElementById('sdc-slots');
      const slots = getSlots();
      if (el) el.textContent = `${slots} cupos`;
      if (sl) sl.textContent = slots.toString();
    }
    // Decrement on lead capture
    const origCapture = SDCChat.captureLead;
    SDCChat.captureLead = function() {
      const current = getSlots();
      if (current > 0) setSlots(current - 1);
      updateSlotsDisplay();
      return origCapture.apply(this, arguments);
    };
    updateSlotsDisplay();

    // Show popup after delay (only if not already captured lead)
    setTimeout(() => {
      if (!state.leadCaptured && !state.popupShown) SDCChat.showPopup();
    }, CONFIG.popupDelay);

    // Scroll trigger popup
    let scrolled = false;
    window.addEventListener('scroll', function () {
      if (!scrolled && window.scrollY > 300) {
        scrolled = true;
        if (!state.leadCaptured && !state.popupShown) SDCChat.showPopup();
      }
    }, { once: true });

    // Exit intent trigger
    document.addEventListener('mouseleave', function (e) {
      if (e.clientY < 0 && !state.popupShown && !state.leadCaptured) {
        SDCChat.showPopup();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
