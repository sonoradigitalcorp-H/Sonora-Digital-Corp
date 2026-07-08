import "clsx";
import { a4 as attr_style, a5 as stringify, a6 as attr, e as escape_html, a3 as derived, a7 as ensure_array_like, a8 as attr_class } from "../../chunks/index.js";
const ALLOWED = {
  idle: ["listening"],
  listening: ["thinking", "idle"],
  thinking: ["executing", "listening", "alert"],
  executing: ["completed", "alert", "thinking"],
  completed: ["idle", "listening"],
  alert: ["idle"]
};
class OrbMachine {
  constructor() {
    this.state = "idle";
    this.message = "";
    this.progress = null;
    this.actions = [];
    this.history = [];
  }
  transition(to, opts) {
    if (!ALLOWED[this.state].includes(to)) return false;
    this.history.push({ from: this.state, to, timestamp: Date.now() });
    this.state = to;
    if (opts?.message !== void 0) this.message = opts.message;
    if (opts?.progress !== void 0) this.progress = opts.progress;
    if (opts?.actions !== void 0) this.actions = opts.actions;
    return true;
  }
  listen() {
    this.transition("listening", { message: "Listening..." });
  }
  think(msg) {
    this.transition("thinking", { message: msg || "Thinking..." });
  }
  execute(msg, p) {
    this.transition("executing", { message: msg, progress: p });
  }
  complete(msg) {
    this.transition("completed", { message: msg, progress: 100 });
  }
  alert(msg) {
    this.transition("alert", { message: msg });
  }
  reset() {
    this.transition("idle", { message: "", progress: null, actions: [] });
  }
}
class KernelClient {
  constructor(url = "ws://localhost:8000/kernel/ws") {
    this.ws = null;
    this.onState = null;
    this.onResult = null;
    this.onError = null;
    this.reconnectTimer = null;
    this.connected = $state(false);
    this.url = url;
  }
  connect() {
    if (this.ws?.readyState === WebSocket.OPEN) return;
    try {
      this.ws = new WebSocket(this.url);
      this.ws.onopen = () => {
        this.connected = true;
      };
      this.ws.onclose = () => {
        this.connected = false;
        this.scheduleReconnect();
      };
      this.ws.onerror = () => {
        this.connected = false;
        this.onError?.("WebSocket error");
      };
      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "orb.state") this.onState?.(data);
          else this.onResult?.(data);
        } catch {
          this.onError?.("Invalid message");
        }
      };
    } catch {
      this.scheduleReconnect();
    }
  }
  send(input) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) return;
    this.ws.send(JSON.stringify({ input, channel: "web", timestamp: (/* @__PURE__ */ new Date()).toISOString() }));
  }
  onStateChange(cb) {
    this.onState = cb;
  }
  onResult(cb) {
    this.onResult = cb;
  }
  onError(cb) {
    this.onError = cb;
  }
  scheduleReconnect() {
    if (this.reconnectTimer) return;
    this.reconnectTimer = setTimeout(() => {
      this.reconnectTimer = null;
      this.connect();
    }, 3e3);
  }
  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer);
    this.ws?.close();
    this.ws = null;
    this.connected = false;
  }
  get isConnected() {
    return this.connected;
  }
}
function Orb($$renderer, $$props) {
  let { state = "idle", message = "", progress = null } = $$props;
  const COLORS = {
    idle: "#a0a0a0",
    listening: "#3b82f6",
    thinking: "#8b5cf6",
    executing: "#f59e0b",
    completed: "#22c55e",
    alert: "#ef4444"
  };
  const color = derived(() => COLORS[state] || COLORS.idle);
  const pulse = derived(() => state === "listening" || state === "thinking");
  const showProgress = derived(() => state === "executing" && progress !== null);
  $$renderer.push(`<div class="orb-container svelte-1s6vqtb"><div class="orb svelte-1s6vqtb"${attr_style(`background: ${stringify(color())}; box-shadow: 0 0 30px ${stringify(color())}40; animation: ${pulse() ? "pulse 2s infinite" : "none"}`)}>`);
  if (showProgress()) {
    $$renderer.push("<!--[0-->");
    $$renderer.push(`<div class="progress-ring svelte-1s6vqtb"><svg viewBox="0 0 36 36" class="progress-svg svelte-1s6vqtb"><path class="progress-bg svelte-1s6vqtb" d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path><path class="progress-fill svelte-1s6vqtb"${attr("stroke-dasharray", `${stringify(progress)}, 100`)} d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"></path></svg></div>`);
  } else {
    $$renderer.push("<!--[-1-->");
  }
  $$renderer.push(`<!--]--></div> `);
  if (message) {
    $$renderer.push("<!--[0-->");
    $$renderer.push(`<p class="orb-message svelte-1s6vqtb">${escape_html(message)}</p>`);
  } else {
    $$renderer.push("<!--[-1-->");
  }
  $$renderer.push(`<!--]--></div>`);
}
function Chat($$renderer, $$props) {
  $$renderer.component(($$renderer2) => {
    let input = "";
    let messages = [];
    const orb = new OrbMachine();
    const kernel = new KernelClient();
    kernel.onStateChange((msg) => {
      orb.transition(msg.state, {
        message: msg.message,
        progress: msg.progress,
        actions: msg.actions
      });
    });
    kernel.onResult((result) => {
      messages = [
        ...messages,
        {
          role: "assistant",
          text: JSON.stringify(result.output || result, null, 2)
        }
      ];
      orb.complete("Done");
      setTimeout(() => orb.reset(), 2e3);
    });
    $$renderer2.push(`<div class="chat-container svelte-z97wf1"><header class="chat-header svelte-z97wf1">`);
    Orb($$renderer2, {
      state: orb.state,
      message: orb.message,
      progress: orb.progress
    });
    $$renderer2.push(`<!----> <h1 class="svelte-z97wf1">Hermes</h1></header> <main class="messages svelte-z97wf1"><!--[-->`);
    const each_array = ensure_array_like(messages);
    for (let $$index = 0, $$length = each_array.length; $$index < $$length; $$index++) {
      let msg = each_array[$$index];
      $$renderer2.push(`<div${attr_class(`message ${stringify(msg.role)}`, "svelte-z97wf1")}>${escape_html(msg.text)}</div>`);
    }
    $$renderer2.push(`<!--]--></main> <footer class="chat-input svelte-z97wf1"><textarea placeholder="Type a message..." rows="1" class="svelte-z97wf1">`);
    const $$body = escape_html(input);
    if ($$body) {
      $$renderer2.push(`${$$body}`);
    }
    $$renderer2.push(`</textarea> <button${attr("disabled", !input.trim(), true)} class="svelte-z97wf1">Send</button></footer></div>`);
  });
}
function _page($$renderer) {
  Chat($$renderer);
}
export {
  _page as default
};
