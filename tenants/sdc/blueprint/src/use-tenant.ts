"use client";
import { createContext, useContext, type ReactNode } from "react";

export interface TenantConfig {
  tenantId: string;
  tenantName: string;
  primaryColor: string;
  accentColor: string;
  logo?: string;
}

const tenants: Record<string, TenantConfig> = {
  "abe-music": {
    tenantId: "bb3b0838-6e53-4d12-af37-0b69ab40c1b3",
    tenantName: "ABE Music",
    primaryColor: "#FFD700",
    accentColor: "#B8860B",
  },
  sdc: {
    tenantId: "2edccb13-3357-40b3-8227-560f397ae585",
    tenantName: "Sonora Digital Corp",
    primaryColor: "#8b5cf6",
    accentColor: "#6d28d9",
  },
};

export const TenantContext = createContext<TenantConfig>(tenants["abe-music"]);

export function TenantProvider({ tenant = "abe-music", children }: { tenant?: string; children: ReactNode }) {
  const config = tenants[tenant] || tenants["abe-music"];
  return <TenantContext.Provider value={config}>{children}</TenantContext.Provider>;
}

export function useTenant() {
  return useContext(TenantContext);
}
