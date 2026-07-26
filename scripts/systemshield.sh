#!/bin/bash
# ═══════════════════════════════════════════════════════════
# SYSTEMSHIELD — Escudo de Seguridad para Mystic OS
# ═══════════════════════════════════════════════════════════
# Ejecutar: sudo bash scripts/systemshield.sh [scan|report|fix]

set -e
MODE="${1:-scan}"

RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
PASS=0; FAIL=0; WARN=0

check() {
    local name="$1" status="$2" msg="$3"
    if [ "$status" = "✅" ]; then echo -e "${GREEN}✅${NC} $name"; PASS=$((PASS+1))
    elif [ "$status" = "⚠️" ]; then echo -e "${YELLOW}⚠️${NC} $name — $msg"; WARN=$((WARN+1))
    else echo -e "${RED}❌${NC} $name — $msg"; FAIL=$((FAIL+1)); fi
}

echo -e "\n${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "${CYAN}  SYSTEMSHIELD — Escudo de Seguridad${NC}"
echo -e "${CYAN}  $(date)${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}\n"

echo -e "${YELLOW}── Capa 1: Firewall ──${NC}"
if sudo ufw status | grep -q "Status: active"; then
    check "UFW activo" "✅"
    PORTS=$(sudo ufw status | grep -c "ALLOW")
    check "Puertos controlados: ${PORTS}" "✅"
else
    check "UFW inactivo" "❌"
fi

echo -e "\n${YELLOW}── Capa 2: Fail2ban ──${NC}"
F2B=$(sudo fail2ban-client status 2>/dev/null | grep "Jail list" | grep -oP '\w+' | wc -l)
if [ "$F2B" -gt 0 ]; then
    check "Fail2ban activo (${F2B} jails)" "✅"
else
    check "Fail2ban inactivo" "❌"
fi

echo -e "\n${YELLOW}── Capa 3: Nginx ──${NC}"
if nginx -t 2>&1 | grep -q "syntax is ok"; then
    check "Config OK" "✅"
else
    check "Config errores" "❌"
fi

echo -e "\n${YELLOW}── Capa 4: Puertos abiertos ──${NC}"
for p in 22 80 443; do
    if ss -tlnp | grep -q ":${p} "; then check "Puerto ${p} (autorizado)" "✅"; else check "Puerto ${p} (cerrado)" "⚠️"; fi
done
for p in 3000 5000 5432 6379 8000 8080 3000 5678 7687 6333 8931; do
    if ss -tlnp | grep -q ":${p} "; then
        PROC=$(ss -tlnp | grep ":${p} " | grep -oP 'users:\(\((.*?)\)\)')
        check "Puerto ${p} (abierto: ${PROC})" "⚠️" "Servicio interno expuesto"
    fi
done

echo -e "\n${YELLOW}── Capa 5: Docker ──${NC}"
if docker ps 2>/dev/null | grep -q "sdc-"; then
    CHECK=$(docker ps --format '{{.Names}} {{.Ports}}' | grep -c "0.0.0.0" || true)
    if [ "$CHECK" -gt 0 ]; then
        check "${CHECK} contenedores expuestos en 0.0.0.0" "⚠️" "Deben estar en 127.0.0.1"
    else
        check "Contenedores seguros" "✅"
    fi
fi

echo -e "\n${YELLOW}── Capa 6: SSL ──${NC}"
if [ -f /etc/letsencrypt/live/sonoradigitalcorp.com/fullchain.pem ]; then
    EXPIRY=$(sudo openssl x509 -in /etc/letsencrypt/live/sonoradigitalcorp.com/fullchain.pem -noout -enddate 2>/dev/null | cut -d= -f2)
    check "SSL vigente (expira: ${EXPIRY})" "✅"
else
    check "SSL no encontrado" "❌"
fi

echo -e "\n${CYAN}══════════════════════════════════════════════════${NC}"
echo -e "  ${GREEN}✅ ${PASS} pasaron${NC} | ${YELLOW}⚠️ ${WARN} advertencias${NC} | ${RED}❌ ${FAIL} fallos${NC}"
echo -e "${CYAN}══════════════════════════════════════════════════${NC}\n"
