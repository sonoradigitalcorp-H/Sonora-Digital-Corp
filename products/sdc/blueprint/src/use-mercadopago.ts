"use client";

const MCP = "/api/mcp/execute";

interface PreferenceOptions {
  title: string;
  unitPrice: number;
  quantity?: number;
  currency?: string;
  externalReference?: string;
  successUrl?: string;
  notificationUrl?: string;
}

interface ProductInfo {
  title: string;
  unitPrice: number;
  artistName: string;
  artistId: string;
  selfieUrl?: string;
}

export function useMercadoPago() {
  const createPreference = async (opts: PreferenceOptions) => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        tool: "mp_create_preference",
        args: {
          title: opts.title,
          unit_price: opts.unitPrice,
          quantity: opts.quantity || 1,
          currency: opts.currency || "MXN",
          external_reference: opts.externalReference || "",
          success_url: opts.successUrl || `${window.location.origin}/gracias`,
          notification_url: opts.notificationUrl || `${window.location.origin}/webhooks/mercadopago`,
        },
      }),
    });
    return resp.json();
  };

  const buyPhoto = async (product: ProductInfo) => {
    const extRef = `user_${Date.now()}:${product.artistId}:foto`;
    const result = await createPreference({
      title: product.title,
      unitPrice: product.unitPrice,
      externalReference: extRef,
    });
    const initPoint = result?.result?.init_point;
    if (initPoint) window.location.href = initPoint;
    return result;
  };

  const getPayment = async (paymentId: string) => {
    const resp = await fetch(MCP, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tool: "mp_get_payment", args: { payment_id: paymentId } }),
    });
    return resp.json();
  };

  return { createPreference, buyPhoto, getPayment };
}
