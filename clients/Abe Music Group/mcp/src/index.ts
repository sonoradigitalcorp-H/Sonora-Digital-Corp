import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";

const HERMES_API_URL = process.env.HERMES_API_URL ?? "http://localhost:8000";
const TENANT_ID = process.env.ABE_MUSIC_TENANT_ID ?? "";
const API_TOKEN = process.env.ABE_MUSIC_API_TOKEN ?? "";

const headers: Record<string, string> = {
  "Content-Type": "application/json",
  ...(API_TOKEN ? { Authorization: `Bearer ${API_TOKEN}` } : {}),
  ...(TENANT_ID ? { "X-Tenant-ID": TENANT_ID } : {}),
};

async function apiGet(path: string): Promise<unknown> {
  const res = await fetch(`${HERMES_API_URL}${path}`, { headers });
  if (!res.ok) {
    throw new Error(`HERMES API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

async function apiPost(path: string, body: unknown): Promise<unknown> {
  const res = await fetch(`${HERMES_API_URL}${path}`, {
    method: "POST",
    headers,
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(`HERMES API error ${res.status}: ${await res.text()}`);
  }
  return res.json();
}

const server = new McpServer({
  name: "abe-music-hub",
  version: "1.0.0",
});

// ── Hub stats ─────────────────────────────────────────────────────────────────
server.tool(
  "get_hub_stats",
  "KPIs del Abe Music Hub: fans registrados, reservas, ingresos, tokens $RESO",
  {},
  async () => {
    const data = await apiGet("/api/v1/hub/stats");
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── Fans ──────────────────────────────────────────────────────────────────────
server.tool(
  "list_fans",
  "Lista fans/clientes registrados en el Hub",
  {
    limit: z.number().int().min(1).max(100).optional().describe("Máximo de resultados (default 20)"),
    offset: z.number().int().min(0).optional().describe("Offset para paginación"),
  },
  async ({ limit = 20, offset = 0 }) => {
    const data = await apiGet(`/api/v1/hub/fans?limit=${limit}&offset=${offset}`);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── Bookings ──────────────────────────────────────────────────────────────────
server.tool(
  "list_bookings",
  "Lista reservas del Hub con estado de pago y servicio",
  {
    estado: z.enum(["pendiente", "confirmada", "cancelada", "completada"]).optional(),
    limit: z.number().int().min(1).max(100).optional(),
  },
  async ({ estado, limit = 20 }) => {
    const qs = new URLSearchParams({ limit: String(limit) });
    if (estado) qs.set("estado", estado);
    const data = await apiGet(`/api/v1/hub/bookings?${qs}`);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── Servicios ─────────────────────────────────────────────────────────────────
server.tool(
  "list_services",
  "Lista servicios disponibles en el Hub (salas, clases, mastering...)",
  {},
  async () => {
    const data = await apiGet("/api/v1/hub/services");
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── Tokens $RESO ──────────────────────────────────────────────────────────────
server.tool(
  "get_token_leaderboard",
  "Top fans por balance de tokens $RESO",
  {
    limit: z.number().int().min(1).max(50).optional(),
  },
  async ({ limit = 10 }) => {
    const data = await apiGet(`/api/v1/hub/leaderboard/weekly?limit=${limit}`);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

server.tool(
  "get_fan_tokens",
  "Balance $RESO de un fan específico",
  {
    fan_id: z.string().uuid().describe("UUID del fan"),
  },
  async ({ fan_id }) => {
    const data = await apiGet(`/api/v1/hub/tokens/balance?fan_id=${fan_id}`);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── Eventos ───────────────────────────────────────────────────────────────────
server.tool(
  "list_events",
  "Eventos próximos del Hub",
  {
    upcoming_only: z.boolean().optional().describe("Solo eventos futuros"),
  },
  async ({ upcoming_only = true }) => {
    const data = await apiGet(`/api/v1/hub/events?upcoming=${upcoming_only}`);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── Suscripciones ─────────────────────────────────────────────────────────────
server.tool(
  "list_subscriptions",
  "Suscripciones activas (básico/pro/élite) y sus fans",
  {
    plan: z.enum(["basico", "pro", "elite"]).optional(),
  },
  async ({ plan }) => {
    const qs = plan ? `?plan=${plan}` : "";
    const data = await apiGet(`/api/v1/hub/subscriptions${qs}`);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── Crear booking (admin) ─────────────────────────────────────────────────────
server.tool(
  "create_booking",
  "Crea una reserva manual en el Hub",
  {
    fan_id: z.string().uuid(),
    service_id: z.string().uuid(),
    fecha: z.string().describe("Fecha YYYY-MM-DD"),
    hora_inicio: z.string().describe("Hora HH:MM"),
    hora_fin: z.string().describe("Hora HH:MM"),
    notas: z.string().optional(),
  },
  async (body) => {
    const data = await apiPost("/api/v1/hub/bookings", body);
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// ── HERMES health ─────────────────────────────────────────────────────────────
server.tool(
  "hermes_health",
  "Verifica que HERMES OS API esté corriendo",
  {},
  async () => {
    const data = await apiGet("/health");
    return { content: [{ type: "text", text: JSON.stringify(data, null, 2) }] };
  }
);

// Boot
const transport = new StdioServerTransport();
await server.connect(transport);
