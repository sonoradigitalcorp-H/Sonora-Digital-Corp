// ── Hooks ──
export { useVoice } from "./use-voice";
export { useMemory } from "./use-memory";
export { useRag } from "./use-rag";
export { useRealtime } from "./use-realtime";
export { useSupabase } from "./use-supabase";
export { useHasura } from "./use-hasura";
export { useMercadoPago } from "./use-mercadopago";
export { useTenant, TenantProvider, TenantContext } from "./use-tenant";

// ── Components ──
export { VoiceWidget } from "./components/VoiceWidget";
export { PurchaseModal } from "./components/PurchaseModal";

// ── Types ──
export type {
  MCPResponse, Product, Artist, MemoryEntry, RAGResult, Transaction, AgentName,
} from "./types";
