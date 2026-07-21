"""
Edge Receiver — VPS endpoint para OpenClaw Edge (Fourgea México)

Recibe archivos del edge client, orquesta el pipeline de procesamiento,
delega en fiscal-agent existente.

Endpoints:
    POST /edge/inbox   — Recibir archivo (XML/PDF) para procesar
    GET  /edge/health  — Health check

Seguridad:
    - API key por dispositivo
    - Rate limiting: 60 req/min por device
    - Solo XML y PDF
    - Tamaño máximo: 20MB
"""

from __future__ import annotations

import hashlib
import logging
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

import httpx
from fastapi import FastAPI, File, Header, HTTPException, Request, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("openclaw.edge.receiver")

FISCAL_AGENT_URL = os.getenv("FISCAL_AGENT_URL", "http://fiscal-agent:8001")
EDGE_API_KEY = os.getenv("EDGE_API_KEY", "openclaw-edge-dev-key")
FISCAL_AGENT_TIMEOUT = float(os.getenv("FISCAL_AGENT_TIMEOUT", "5.0"))
MAX_FILE_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {".xml", ".pdf", ".XML", ".PDF"}

NS_CFDI = "http://www.sat.gob.mx/cfd/4"
NS_TFD = "http://www.sat.gob.mx/TimbreFiscalDigital"

_rate_limits: dict[str, list[float]] = {}

app = FastAPI(title="OpenClaw Edge Receiver", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


def _check_rate_limit(device_id: str, max_rpm: int = 60) -> None:
    now = time.time()
    window = now - 60
    timestamps = _rate_limits.get(device_id, [])
    timestamps = [t for t in timestamps if t > window]
    if len(timestamps) >= max_rpm:
        raise HTTPException(status_code=429, detail="Rate limit exceeded. Max 60 req/min.")
    timestamps.append(now)
    _rate_limits[device_id] = timestamps


def _verify_api_key(authorization: str | None) -> str:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Bearer token")
    token = authorization.removeprefix("Bearer ").strip()
    if token != EDGE_API_KEY:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API key")
    return token


def _parse_cfdi_xml(content: bytes, filename: str) -> dict:
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        return {"valid": False, "errors": [f"XML malformado: {e}"]}

    ns = {"cfdi": NS_CFDI, "tfd": NS_TFD}
    comprobante = root.find("cfdi:Comprobante", ns)
    if comprobante is None:
        comprobante = root
    elif root.tag == f"{{{NS_CFDI}}}Comprobante":
        comprobante = root

    def _tag(path: str) -> str:
        for prefix, uri in ns.items():
            path = path.replace(f"{prefix}:", f"{{{uri}}}")
        return path

    data: dict = {
        "filename": filename,
        "valid": True,
        "errors": [],
        "version": comprobante.get("Version", "?"),
        "tipo": comprobante.get("TipoDeComprobante", "?").upper(),
        "fecha": comprobante.get("Fecha", "?"),
        "rfc_emisor": comprobante.get("RfcEmisor", comprobante.get("RfcEmisora", "?")),
        "rfc_receptor": comprobante.get("RfcReceptor", comprobante.get("RfcReceptora", "?")),
        "nombre_emisor": comprobante.get("NombreEmisor", ""),
        "nombre_receptor": comprobante.get("NombreReceptor", ""),
        "subtotal": _to_float(comprobante.get("SubTotal", "0")),
        "total": _to_float(comprobante.get("Total", "0")),
        "moneda": comprobante.get("Moneda", "MXN"),
        "uuid": "",
        "conceptos": [],
        "impuestos": {},
    }

    tfd = root.find(".//tfd:TimbreFiscalDigital", ns)
    if tfd is not None:
        data["uuid"] = tfd.get("UUID", "")

    conceptos_node = comprobante.find("cfdi:Conceptos", ns)
    if conceptos_node is not None:
        for c in conceptos_node.findall("cfdi:Concepto", ns):
            concepto = {
                "clave": c.get("ClaveProdServ", ""),
                "descripcion": c.get("Descripcion", ""),
                "cantidad": _to_float(c.get("Cantidad", "1")),
                "valor_unitario": _to_float(c.get("ValorUnitario", "0")),
                "importe": _to_float(c.get("Importe", "0")),
            }
            impuestos_node = c.find("cfdi:Impuestos", ns)
            if impuestos_node is not None:
                traslados = impuestos_node.findall("cfdi:Traslados/cfdi:Traslado", ns)
                concepto["tasas_iva"] = [t.get("TasaOCuota", "?") for t in traslados if t.get("Impuesto") == "002"]
                retenciones = impuestos_node.findall("cfdi:Retenciones/cfdi:Retencion", ns)
                concepto["retenciones"] = [r.get("TasaOCuota", "?") for r in retenciones]
            data["conceptos"].append(concepto)

    impuestos = comprobante.find("cfdi:Impuestos", ns)
    if impuestos is not None:
        data["impuestos"]["total_traslados"] = _to_float(impuestos.get("TotalImpuestosTrasladados", "0"))
        data["impuestos"]["total_retenciones"] = _to_float(impuestos.get("TotalImpuestosRetenidos", "0"))

    data["iva"] = round(data["total"] - data["subtotal"], 2)

    rfc_re = re.compile(r"^[A-Z&Ñ]{3,4}\d{6}[A-Z0-9]{3}$")
    if not rfc_re.match(data["rfc_emisor"]):
        data["valid"] = False
        data["errors"].append(f"RFC emisor inválido: {data['rfc_emisor']}")
    if not rfc_re.match(data["rfc_receptor"]):
        data["valid"] = False
        data["errors"].append(f"RFC receptor inválido: {data['rfc_receptor']}")

    if data["total"] < 0:
        data["valid"] = False
        data["errors"].append(f"Total negativo: {data['total']}")

    return data


def _to_float(val: str) -> float:
    try:
        return float(val)
    except (ValueError, TypeError):
        return 0.0


def _classify_cfdi(data: dict) -> str:
    tipo = data.get("tipo", "").upper()
    if tipo == "I":
        return "ingreso"
    elif tipo == "E":
        return "egreso"
    elif tipo == "P":
        return "nomina"
    elif tipo == "T":
        return "traslado"
    elif tipo == "N":
        return "nomina"
    return "otro"


def _generate_filename(data: dict) -> str:
    rfc = data.get("rfc_emisor", "SINRFC")
    fecha_raw = data.get("fecha", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    fecha = fecha_raw[:10].replace("-", "")
    tipo = _classify_cfdi(data).upper()
    uuid_short = (data.get("uuid") or "SINUUID")[:8]
    ext = ".xml"
    return f"{rfc}_{fecha}_{tipo}_{uuid_short}{ext}"


async def _call_fiscal_agent(operation: str, xml_content: dict, device_id: str) -> dict:
    try:
        async with httpx.AsyncClient(timeout=FISCAL_AGENT_TIMEOUT) as client:
            resp = await client.post(
                f"{FISCAL_AGENT_URL}/operate",
                json={
                    "operation": operation,
                    "inputs": {"json_content": xml_content},
                    "tenant_id": device_id,
                },
            )
            resp.raise_for_status()
            return resp.json()
    except httpx.TimeoutException:
        return {"success": False, "error": "Fiscal Agent timeout", "data": None}
    except Exception as e:
        logger.warning(f"Fiscal agent unavailable: {e}")
        return {"success": False, "error": f"Fiscal agent error: {e}", "data": None}


@app.post("/edge/inbox")
async def inbox_upload(
    request: Request,
    file: UploadFile = File(...),
    authorization: str | None = Header(None),
    x_device_id: str | None = Header(None, alias="X-Device-ID"),
):
    device_id = x_device_id or "unknown"
    _verify_api_key(authorization)
    _check_rate_limit(device_id)

    ext = Path(file.filename or "unknown").suffix
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"Extensión no permitida: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail=f"Archivo excede {MAX_FILE_SIZE // (1024*1024)}MB")

    ts = datetime.now(timezone.utc).isoformat()
    file_hash = hashlib.sha256(content).hexdigest()

    if ext.lower() == ".xml":
        parsed = _parse_cfdi_xml(content, file.filename)
        if parsed["errors"]:
            logger.warning(f"CFDI con errores: {file.filename} — {parsed['errors']}")

        fiscal_result = await _call_fiscal_agent("validate_cfdi", parsed, device_id)
        classification = _classify_cfdi(parsed)
        new_name = _generate_filename(parsed)

        result = {
            "success": parsed["valid"],
            "file": file.filename,
            "hash": file_hash,
            "timestamp": ts,
            "classification": classification,
            "renamed_to": new_name,
            "result": parsed,
            "fiscal_validation": fiscal_result.get("data") if fiscal_result.get("success") else None,
            "errors": parsed["errors"] if not parsed["valid"] else [],
        }
    elif ext.lower() == ".pdf":
        result = {
            "success": True,
            "file": file.filename,
            "hash": file_hash,
            "timestamp": ts,
            "classification": "pdf_pendiente_ocr",
            "result": {"filename": file.filename, "size_bytes": len(content), "ocr_pending": True},
            "message": "PDF recibido. OCR pendiente de implementación.",
        }
    else:
        raise HTTPException(status_code=400, detail=f"Tipo no soportado: {ext}")

    logger.info(f"Procesado: {file.filename} → {result.get('classification', '?')} (success={result['success']})")
    return result


@app.get("/edge/health")
async def health():
    return {"status": "ok", "version": "1.0.0", "fiscal_agent_url": FISCAL_AGENT_URL}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=18990, log_level="info")
