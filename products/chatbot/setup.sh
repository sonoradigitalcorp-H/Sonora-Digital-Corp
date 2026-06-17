#!/bin/bash
# Configurador de Chatbot WhatsApp para negocios locales
# Uso: bash setup.sh "Nombre del Negocio" "descripción" "teléfono"
set -euo pipefail

NEGOCIO="${1:-Mi Negocio}"
DESCRIPCION="${2:-Ofrecemos servicios profesionales}"
TELEFONO="${3:-+526621234567}"
PROMPT_FILE="prompt.txt"

echo "=== Configurando chatbot para: $NEGOCIO ==="

# 1. Generar prompt personalizado
cat > "$PROMPT_FILE" << PROMPTEOF
Eres el asistente virtual de $NEGOCIO.
$DESCRIPCION

REGLAS:
- Respondes SOLO en horario laboral (9:00-18:00)
- Fuera de horario: "Gracias por contactarnos. Te atenderemos en horario laboral (9am-6pm)"
- Si preguntan precios: "Los precios varían según el servicio. Te recomiendo agendar una llamada"
- Si preguntan por ubicación: dices la dirección y horarios
- Si quieren agendar: pides nombre, teléfono, fecha, y dices "Te confirmamos tu cita en breve"
- Siempre eres amable y profesional
- No inventes información que no tengas
- Si no sabes algo: "Déjame consultar con el equipo y te respondo al instante"

SERVICIOS:
- [Lista de servicios principales]

HORARIO:
- Lunes a Viernes: 9:00 - 18:00
- Sábados: 9:00 - 14:00

UBICACIÓN:
- [Dirección del negocio]

REDES:
- WhatsApp: $TELEFONO
- Instagram: @[usuario]
PROMPTEOF

echo "✅ Prompt generado: $PROMPT_FILE"
echo ""
echo "=== SIGUIENTES PASOS ==="
echo ""
echo "1. Edita el prompt con los datos reales:"
echo "   nano $PROMPT_FILE"
echo ""
echo "2. Copia el prompt a Hermes:"
echo "   curl -X POST http://localhost:8000/api/bot/config \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"business\":\"$NEGOCIO\",\"prompt\":\"$(cat $PROMPT_FILE | tr '\n' ' ')\"}'"
echo ""
echo "3. Comparte el número de WhatsApp con tus clientes:"
echo "   wa.me/$TELEFONO"
echo ""
echo "=== LISTO ==="
