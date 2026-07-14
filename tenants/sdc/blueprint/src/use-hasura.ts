"use client";
import type { Artist, Product, Transaction } from "./types";

const MCP = "/api/mcp/execute";

export function useHasura() {
  const query = async (graphqlQuery: string) => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool: "hasura_query", args: { query: graphqlQuery } }),
    });
    return resp.json();
  };

  const mutate = async (graphqlMutation: string) => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool: "hasura_mutate", args: { mutation: graphqlMutation } }),
    });
    return resp.json();
  };

  const getArtists = async (): Promise<Artist[]> => {
    const data = await query("{ artists(order_by: {created_at: asc}) { id name streams revenue followers status } }");
    return data?.result?.data?.artists || [];
  };

  const getProducts = async (): Promise<Product[]> => {
    const data = await query("{ products(where: {active: {_eq: true}}) { id name description price_mxn type requires_lora artist { name } } }");
    return data?.result?.data?.products || [];
  };

  const getTransactions = async (limit = 20): Promise<Transaction[]> => {
    const data = await query(`{ transactions(order_by: {created_at: desc}, limit: ${limit}) { id amount status delivery_url provider description metadata } }`);
    return data?.result?.data?.transactions || [];
  };

  return { query, mutate, getArtists, getProducts, getTransactions };
}
