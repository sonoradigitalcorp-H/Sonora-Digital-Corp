export interface MCPResponse<T = any> {
  result: T | { error: string };
}

export interface Product {
  id: string;
  name: string;
  description?: string;
  price_mxn: number;
  type: "foto" | "playera" | "video";
  requires_lora: boolean;
  artist?: { name: string };
}

export interface Artist {
  id: string;
  name: string;
  streams: number;
  revenue: number;
  followers?: number;
  status: string;
}

export interface MemoryEntry {
  key: string;
  value: string;
  user_id?: string;
  layer?: number;
  importance?: number;
  tags?: string;
  access_count?: number;
  created_at?: number;
}

export interface RAGResult {
  id: string;
  score: number;
  payload?: { content: string; document_id: string; tags?: string };
}

export interface Transaction {
  id: string;
  amount: number;
  status: string;
  delivery_url?: string;
  provider?: string;
  description?: string;
  metadata?: Record<string, any>;
}

export type AgentName =
  | "ceo" | "marketing" | "content" | "sales" | "support" | "voice"
  | "creator" | "quality" | "monitor";
