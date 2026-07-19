"""Cyber Diagnosis Express — Scan Engine
Checks comunes de ciberseguridad para empresas (no invasivo).
"""
import datetime
import json
import subprocess
import ssl
import socket
from pathlib import Path
from urllib.parse import urlparse

import httpx

CHECKS = []


def check(name, category, severity, description):
    def decorator(func):
        CHECKS.append({
            "name": name,
            "category": category,
            "severity": severity,
            "description": description,
            "func": func,
        })
        return func
    return decorator


# ─── DNS & Domain ───

@check("DNSSEC", "DNS", "alta", "Verifica si el dominio tiene DNSSEC habilitado")
def check_dnssec(domain: str) -> dict:
    r = subprocess.run(
        ["dig", domain, "DNSKEY", "+short"],
        capture_output=True, text=True, timeout=10,
    )
    has_dnssec = bool(r.stdout.strip())
    return {
        "status": "ok" if has_dnssec else "warning",
        "detail": "DNSSEC activo" if has_dnssec else "Sin DNSSEC — vulnerable a spoofing",
    }


@check("SPF Record", "DNS", "media", "Verifica registro SPF contra spoofing")
def check_spf(domain: str) -> dict:
    r = subprocess.run(
        ["dig", "TXT", domain, "+short"],
        capture_output=True, text=True, timeout=10,
    )
    records = r.stdout.strip().split("\n")
    spf = [l for l in records if "v=spf1" in l]
    return {
        "status": "ok" if spf else "error",
        "detail": f"SPF presente: {spf[0][:80]}..." if spf else "Sin SPF — cualquiera puede enviar emails como tu dominio",
    }


@check("DMARC Record", "DNS", "alta", "Verifica DMARC contra phishing")
def check_dmarc(domain: str) -> dict:
    r = subprocess.run(
        ["dig", "TXT", f"_dmarc.{domain}", "+short"],
        capture_output=True, text=True, timeout=10,
    )
    records = r.stdout.strip().split("\n")
    dmarc = [l for l in records if "v=DMARC1" in l]
    if dmarc:
        policy = "p=none" if "p=none" in dmarc[0] else "p=quarantine" if "p=quarantine" in dmarc[0] else "p=reject"
        return {
            "status": "warning" if policy == "p=none" else "ok",
            "detail": f"DMARC presente — política: {policy}" + (" (monitoreo, sin protección)" if policy == "p=none" else ""),
        }
    return {"status": "error", "detail": "Sin DMARC — vulnerable a phishing de dominio"}


# ─── SSL/TLS ───

@check("SSL Certificate", "SSL/TLS", "critica", "Verifica vigencia y validez del certificado SSL")
def check_ssl(domain: str) -> dict:
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((domain, 443), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                cert = ssock.getpeercert()
                expires = datetime.datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                days_left = (expires - datetime.datetime.now()).days
                issuer = dict(cert["issuer"])[("organizationName", "O")][0] if ("organizationName", "O") in dict(cert["issuer"]) else "Desconocido"
                return {
                    "status": "ok" if days_left > 30 else "warning" if days_left > 0 else "error",
                    "detail": f"Válido hasta {expires.strftime('%Y-%m-%d')} ({days_left} días) — Emisor: {issuer}",
                }
    except Exception as e:
        return {"status": "error", "detail": f"No se pudo verificar SSL: {str(e)[:80]}"}


@check("HTTPS Redirect", "SSL/TLS", "media", "Verifica redirección HTTP → HTTPS")
def check_https_redirect(domain: str) -> dict:
    try:
        r = httpx.get(f"http://{domain}", follow_redirects=True, timeout=10)
        final_url = str(r.url)
        is_https = final_url.startswith("https")
        return {
            "status": "ok" if is_https else "error",
            "detail": f"Redirige a HTTPS: {final_url[:60]}" if is_https else f"No redirige a HTTPS — {final_url[:60]}",
        }
    except Exception as e:
        return {"status": "warning", "detail": f"No se pudo verificar redirect: {str(e)[:60]}"}


# ─── Security Headers ───

@check("Security Headers", "Headers", "media", "Verifica headers de seguridad HTTP")
def check_security_headers(domain: str) -> dict:
    try:
        r = httpx.get(f"https://{domain}", timeout=10)
        headers = r.headers
        findings = []
        good = 0
        total = 5

        if "Strict-Transport-Security" in headers:
            good += 1; findings.append("✅ HSTS")
        else: findings.append("❌ HSTS")
        if "X-Frame-Options" in headers:
            good += 1; findings.append("✅ X-Frame-Options")
        else: findings.append("❌ X-Frame-Options (clickjacking)")
        if "X-Content-Type-Options" in headers:
            good += 1; findings.append("✅ X-Content-Type-Options")
        else: findings.append("❌ X-Content-Type-Options")
        if "Content-Security-Policy" in headers:
            good += 1; findings.append("✅ CSP")
        else: findings.append("❌ CSP")
        if "Referrer-Policy" in headers:
            good += 1; findings.append("✅ Referrer-Policy")
        else: findings.append("❌ Referrer-Policy")

        score = int((good / total) * 100)
        return {
            "status": "ok" if score >= 80 else "warning" if score >= 40 else "error",
            "detail": f"Score: {score}% — {' '.join(findings)}",
        }
    except Exception as e:
        return {"status": "warning", "detail": f"No se pudieron verificar headers: {str(e)[:60]}"}


# ─── Email ───

@check("Email Security", "Email", "alta", "Verifica config de email contra spoofing")
def check_email(domain: str) -> dict:
    r = subprocess.run(
        ["dig", "MX", domain, "+short"],
        capture_output=True, text=True, timeout=10,
    )
    mx = r.stdout.strip().split("\n")
    mx = [m for m in mx if m.strip()]
    return {
        "status": "ok" if mx else "warning",
        "detail": f"MX records: {len(mx)} servidores de correo" if mx else "Sin MX — el correo podría no funcionar",
    }


@check("Open Ports", "Red", "media", "Escanea puertos comunes expuestos")
def check_ports(domain: str) -> dict:
    common_ports = [22, 80, 443, 8080, 8443, 3306, 5432, 6379, 27017]
    open_ports = []
    for port in common_ports:
        try:
            with socket.create_connection((domain, port), timeout=3):
                open_ports.append(port)
        except (socket.timeout, ConnectionRefusedError, OSError):
            pass
    risky = [p for p in open_ports if p in (3306, 5432, 6379, 27017, 22)]
    return {
        "status": "error" if risky else "ok" if len(open_ports) <= 3 else "warning",
        "detail": f"Puertos abiertos: {open_ports}" + (f" — ¡Riesgo: {risky} expuestos!" if risky else ""),
    }


# ─── Scanner ───

def scan_domain(domain: str) -> dict:
    """Ejecuta todos los checks contra un dominio."""
    results = []
    for check_def in CHECKS:
        try:
            result = check_def["func"](domain)
            results.append({
                "name": check_def["name"],
                "category": check_def["category"],
                "severity": check_def["severity"],
                "description": check_def["description"],
                **result,
            })
        except Exception as e:
            results.append({
                "name": check_def["name"],
                "category": check_def["category"],
                "severity": check_def["severity"],
                "description": check_def["description"],
                "status": "error",
                "detail": f"Error en scan: {str(e)[:80]}",
            })

    score = _calculate_score(results)
    return {
        "domain": domain,
        "score": score,
        "grade": _grade(score),
        "scanned_at": datetime.datetime.now().isoformat(),
        "checks": results,
        "summary": _summarize(results),
    }


def _calculate_score(results: list) -> int:
    weights = {"critica": 25, "alta": 15, "media": 10}
    scores = {"ok": 1.0, "warning": 0.5, "error": 0}
    total = 0
    max_total = 0
    for r in results:
        w = weights.get(r["severity"], 10)
        s = scores.get(r["status"], 0)
        total += w * s
        max_total += w
    return int((total / max_total) * 100) if max_total else 0


def _grade(score: int) -> str:
    if score >= 90: return "A"
    if score >= 75: return "B"
    if score >= 55: return "C"
    if score >= 35: return "D"
    return "F"


def _summarize(results: list) -> dict:
    return {
        "total": len(results),
        "ok": sum(1 for r in results if r["status"] == "ok"),
        "warning": sum(1 for r in results if r["status"] == "warning"),
        "error": sum(1 for r in results if r["status"] == "error"),
        "criticos": [r["name"] for r in results if r["severity"] == "critica" and r["status"] != "ok"],
    }
