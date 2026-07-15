import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

const ABE_API = "http://127.0.0.1:5180";

const server = new Server(
  { name: "abe-service", version: "1.0.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler("tools/list", async () => ({
  tools: [
    {
      name: "abe_get_artist_revenue",
      description: "Revenue de un artista en un mes/año específico",
      inputSchema: {
        type: "object",
        properties: {
          artist_id: { type: "string" },
          month: { type: "number" },
          year: { type: "number" }
        },
        required: ["artist_id", "month", "year"]
      }
    },
    {
      name: "abe_list_artists",
      description: "Lista todos los artistas del sello",
      inputSchema: { type: "object", properties: {} }
    },
    {
      name: "abe_get_contract",
      description: "Contrato de un artista (split, términos)",
      inputSchema: {
        type: "object",
        properties: { artist_id: { type: "string" } },
        required: ["artist_id"]
      }
    },
    {
      name: "abe_search_knowledge",
      description: "Busca en knowledge base del sello",
      inputSchema: {
        type: "object",
        properties: { query: { type: "string" } },
        required: ["query"]
      }
    },
    {
      name: "abe_create_booking",
      description: "Crea una reserva en el hub",
      inputSchema: {
        type: "object",
        properties: {
          service: { type: "string" },
          date: { type: "string" },
          client_name: { type: "string" },
          duration_hours: { type: "number" }
        },
        required: ["service", "date", "client_name"]
      }
    }
  ]
}));

server.setRequestHandler("tools/call", async (req) => {
  const { name, arguments: args } = req.params;
  try {
    const res = await fetch(`${ABE_API}/api/tools/${name}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(args || {})
    });
    const data = await res.json();
    return { content: [{ type: "text", text: JSON.stringify(data) }] };
  } catch (e) {
    return { content: [{ type: "text", text: JSON.stringify({ error: e.message }) }] };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
