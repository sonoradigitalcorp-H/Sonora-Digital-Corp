"use client";
import { useState, useCallback } from "react";
import type { RAGResult } from "./types";

interface RAGOptions {
  tenantId: string;
}

export function useRag(opts: RAGOptions) {
  const [loading, setLoading] = useState(false);

  const search = useCallback(async (query: string, limit = 5): Promise<RAGResult[]> => {
    setLoading(true);
    try {
      const resp = await fetch("/api/mcp/execute", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "rag_search",
          args: { tenant_id: opts.tenantId, query, limit },
        }),
      });
      const data = await resp.json();
      return data?.result?.results || [];
    } catch { return []; }
    finally { setLoading(false); }
  }, [opts.tenantId]);

  const contextFor = useCallback(async (query: string): Promise<string> => {
    const results = await search(query, 3);
    return results.map((r) => r.payload?.content || "").filter(Boolean).join("\n");
  }, [search]);

  return { search, contextFor, loading };
}
