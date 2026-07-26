#!/bin/bash
# =============================================================================
# SETUP SSH NOEL → VPS SDC
# =============================================================================
# Ejecutar en la máquina de Noel para configurar acceso SSH al VPS.
#
# Uso:
#   chmod +x setup-noel-ssh.sh
#   ./setup-noel-ssh.sh
# =============================================================================

VPS_IP="149.56.46.173"
VPS_USER="noel"
VPS_PASS="SdcNoel2026!"
SSH_DIR="$HOME/.ssh"
KEY_NAME="id_ed25519_sdc"

echo "🔧 Configurando acceso SSH a VPS SDC..."

# 1. Crear directorio .ssh si no existe
mkdir -p "$SSH_DIR"
chmod 700 "$SSH_DIR"

# 2. Generar clave SSH si no existe
if [ ! -f "$SSH_DIR/$KEY_NAME" ]; then
    echo "📝 Generando clave SSH..."
    ssh-keygen -t ed25519 -C "noel@sonoradigital" -f "$SSH_DIR/$KEY_NAME" -N ""
    echo "✅ Clave generada: $SSH_DIR/$KEY_NAME"
else
    echo "✅ Clave ya existe: $SSH_DIR/$KEY_NAME"
fi

# 3. Copiar clave pública al VPS (usa password la primera vez)
echo "📤 Subiendo clave pública al VPS..."
ssh-copy-id -i "$SSH_DIR/$KEY_NAME.pub" -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" 2>/dev/null

# 4. Probar conexión
echo "🔍 Probando conexión..."
if ssh -i "$SSH_DIR/$KEY_NAME" -o StrictHostKeyChecking=no "$VPS_USER@$VPS_IP" "echo '✅ Conexión exitosa!'" 2>/dev/null; then
    echo ""
    echo "=========================================="
    echo "✅ ¡SSH configurado correctamente!"
    echo "=========================================="
    echo ""
    echo "Para conectarte al VPS:"
    echo "  ssh -i $SSH_DIR/$KEY_NAME $VPS_USER@$VPS_IP"
    echo ""
    echo "Para migrar tus repos:"
    echo "  cd /home/noel/sonora-digital-corp"
    echo "  ./scripts/migrate-noel-repos.sh"
    echo ""
else
    echo "❌ Error en la conexión. Verifica:"
    echo "  1. Que la IP sea correcta: $VPS_IP"
    echo "  2. Que tengas internet"
    echo "  3. Que el password sea correcto: $VPS_PASS"
fi
