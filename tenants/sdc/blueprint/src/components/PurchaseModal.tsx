"use client";
import { useState, useCallback } from "react";
import { useMercadoPago } from "../use-mercadopago";
import type { Product, Artist } from "../types";

interface PurchaseModalProps {
  product: Product;
  artist: Artist;
  onClose: () => void;
}

export function PurchaseModal({ product, artist, onClose }: PurchaseModalProps) {
  const [selfieFile, setSelfieFile] = useState<File | null>(null);
  const [selfiePreview, setSelfiePreview] = useState<string>("");
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");
  const mp = useMercadoPago();

  const handleFile = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith("image/")) { setError("Solo imágenes JPG o PNG"); return; }
    if (file.size > 10 * 1024 * 1024) { setError("Máximo 10MB"); return; }
    setSelfieFile(file);
    setSelfiePreview(URL.createObjectURL(file));
    setError("");
  }, []);

  const handleBuy = useCallback(async () => {
    if (!selfieFile) { setError("Sube una selfie primero"); return; }
    setUploading(true);
    setError("");

    try {
      // Convert to base64
      const b64 = await new Promise<string>((resolve) => {
        const reader = new FileReader();
        reader.onload = () => resolve((reader.result as string).split(",")[1]);
        reader.readAsDataURL(selfieFile);
      });

      // Upload selfie
      const selfiePath = `selfies/${Date.now()}_${artist.name.replace(/\s+/g, "_")}.jpg`;
      const uploadResp = await fetch("/api/mcp/execute", {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          tool: "upload_file",
          args: { bucket: "sdc-assets", path: selfiePath, content_b64: b64, content_type: selfieFile.type },
        }),
      });
      const uploadData = await uploadResp.json();
      const selfieUrl = uploadData?.result?.url;

      // Create MP preference and redirect
      await mp.buyPhoto({
        title: product.name,
        unitPrice: product.price_mxn,
        artistName: artist.name,
        artistId: artist.id,
        selfieUrl,
      });
    } catch {
      setError("Error al procesar la compra. Intenta de nuevo.");
    }
    setUploading(false);
  }, [selfieFile, product, artist, mp]);

  const prices: Record<string, string> = { foto: "digital", playera: "física", video: "digital" };

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 300,
      display: "flex", alignItems: "center", justifyContent: "center",
      background: "rgba(0,0,0,0.7)", backdropFilter: "blur(8px)",
    }}>
      <div style={{
        background: "#111", borderRadius: "20px", padding: "2rem",
        maxWidth: "420px", width: "90%", border: "1px solid rgba(255,255,255,0.08)",
      }}>
        <h2 style={{ fontSize: "1.2rem", fontWeight: 600, marginBottom: "0.5rem" }}>{product.name}</h2>
        <p style={{ fontSize: "0.85rem", color: "rgba(255,255,255,0.5)", marginBottom: "1.5rem" }}>
          {artist.name} · ${product.price_mxn} MXN · Entrega {prices[product.type] || "digital"}
        </p>

        {selfiePreview ? (
          <div style={{ marginBottom: "1rem" }}>
            <img src={selfiePreview} alt="Tu selfie" style={{ width: "100%", maxHeight: "200px", objectFit: "cover", borderRadius: "12px" }} />
          </div>
        ) : (
          <label style={{
            display: "block", border: "2px dashed rgba(255,255,255,0.15)", borderRadius: "12px",
            padding: "2rem", textAlign: "center", cursor: "pointer", marginBottom: "1rem",
          }}>
            <p style={{ fontSize: "0.85rem", color: "rgba(255,255,255,0.5)" }}>📸 Sube tu selfie aquí</p>
            <p style={{ fontSize: "0.75rem", color: "rgba(255,255,255,0.3)" }}>JPG o PNG · Máximo 10MB</p>
            <input type="file" accept="image/*" onChange={handleFile} style={{ display: "none" }} />
          </label>
        )}

        {error && <p style={{ color: "#ff4444", fontSize: "0.8rem", marginBottom: "1rem" }}>{error}</p>}

        <div style={{ display: "flex", gap: "0.5rem" }}>
          <button onClick={handleBuy} disabled={uploading || !selfieFile}
            style={{
              flex: 1, padding: "0.8rem", borderRadius: "12px", border: "none",
              background: uploading ? "#666" : "linear-gradient(135deg, #FFD700, #B8860B)",
              color: "#000", cursor: uploading ? "not-allowed" : "pointer", fontWeight: 600,
              fontSize: "0.9rem",
            }}>
            {uploading ? "Procesando..." : `Pagar $${product.price_mxn} MXN`}
          </button>
          <button onClick={onClose}
            style={{
              padding: "0.8rem 1.2rem", borderRadius: "12px", border: "1px solid rgba(255,255,255,0.1)",
              background: "transparent", color: "rgba(255,255,255,0.7)", cursor: "pointer",
            }}>
            Cancelar
          </button>
        </div>
      </div>
    </div>
  );
}
