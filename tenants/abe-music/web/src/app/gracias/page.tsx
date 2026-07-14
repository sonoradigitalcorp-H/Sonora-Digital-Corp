"use client";
import { useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

export default function GraciasPage() {
  const params = useSearchParams();
  const status = params.get("status") || "approved";
  const [photoUrl, setPhotoUrl] = useState("");

  useEffect(() => {
    if (status === "approved") {
      const collection_id = params.get("collection_id");
      if (collection_id) {
        fetch("/api/mcp/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            tool: "mp_get_payment",
            args: { payment_id: collection_id },
          }),
        })
          .then((r) => r.json())
          .then((d) => {
            const tx = d?.result;
            if (tx?.status === "approved") {
              setPhotoUrl("https://jibalggzudkflwzdndqz.supabase.co/storage/v1/object/public/sdc-assets/content/loading.jpg");
            }
          })
          .catch(() => {});
      }
      // Poll for photo delivery
      const interval = setInterval(async () => {
        const ref = params.get("external_reference") || "";
        if (!ref) return;
        const resp = await fetch("/api/mcp/execute", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            tool: "hasura_query",
            args: {
              query: `query { transactions(where: {provider_transaction_id: {_eq: "${collection_id}"}}) { metadata delivery_url } }`,
            },
          }),
        });
        const data = await resp.json();
        const url = data?.result?.data?.transactions?.[0]?.delivery_url;
        if (url) {
          setPhotoUrl(url);
          clearInterval(interval);
        }
      }, 3000);
      return () => clearInterval(interval);
    }
  }, [status, params]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-950 p-4">
      <div className="max-w-md w-full glass rounded-2xl p-8 text-center">
        {status === "approved" ? (
          <>
            <div className="text-6xl mb-4">🎉</div>
            <h1 className="text-2xl font-bold text-amber-300 mb-2">¡Gracias por tu compra!</h1>
            <p className="text-gray-400 mb-6">Tu foto se está generando... esto toma unos segundos</p>

            {photoUrl ? (
              <div className="mb-6">
                <img src={photoUrl} alt="Tu foto personalizada" className="w-full rounded-xl mb-4" />
                <a href={photoUrl} download
                  className="inline-block px-6 py-3 bg-amber-500/20 text-amber-300 rounded-xl border border-amber-500/30 hover:bg-amber-500/30 transition-all">
                  📥 Descargar foto
                </a>
              </div>
            ) : (
              <div className="mb-6">
                <div className="w-full h-64 bg-gray-900 rounded-xl animate-pulse flex items-center justify-center text-gray-700">
                  Generando...
                </div>
              </div>
            )}

            <div className="flex gap-2 justify-center">
              <button onClick={() => window.location.href = "/"} className="px-4 py-2 bg-gray-800 text-gray-300 rounded-xl text-sm">
                Volver al inicio
              </button>
            </div>
          </>
        ) : status === "pending" ? (
          <>
            <div className="text-6xl mb-4">⏳</div>
            <h1 className="text-2xl font-bold text-yellow-300 mb-2">Pago pendiente</h1>
            <p className="text-gray-400 mb-4">Recibirás tu foto cuando el pago se confirme</p>
            <Link href="/" className="text-amber-400 hover:text-amber-300">Volver al inicio</Link>
          </>
        ) : (
          <>
            <div className="text-6xl mb-4">❌</div>
            <h1 className="text-2xl font-bold text-red-300 mb-2">Pago no completado</h1>
            <p className="text-gray-400 mb-4">Intenta de nuevo con otro método de pago</p>
            <Link href="/" className="text-amber-400 hover:text-amber-300">Volver al inicio</Link>
          </>
        )}
      </div>
    </div>
  );
}
