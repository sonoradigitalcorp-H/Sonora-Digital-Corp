#!/usr/bin/env bash
# gen_reel_hermosillo.sh — Genera reel vertical (1080x1920) con marca Hermosillo
# usando las fotos FAL existentes. Cortes cada 4-6s (dopamina), zoom sutil,
# texto overlay con beneficios, cierre con CTA.
#
# Requisitos: ffmpeg 7+ (local, NO VPS). Fotos en 03_Media_Assets/photos/
# Uso: bash gen_reel_hermosillo.sh
set -euo pipefail

PHOTOS_DIR="$(cd "$(dirname "$0")/../03_Media_Assets/photos" && pwd)"
OUT="$PHOTOS_DIR/reel_hermosillo.mp4"
W=1080; H=1920
FONT="${FONT:-/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf}"
[ -f "$FONT" ] || FONT="$(fc-match -f '%{file}' 'DejaVu Sans Bold' 2>/dev/null || echo '')"

# Escala+recorte a vertical y añade zoom sutil (zoompan)
# segmento: foto → 6s @ 30fps con zoompan → overlay texto → concat
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

declare -A SEGS=(
  ["contadora_1"]="Contabilidad en orden"
  ["citas_sat"]="Citas SAT gestionadas"
  ["declaracion"]="Declaraciones sin errores"
  ["vision_celular_asistente"]="Asistente IA 24/7"
  ["vision_dashboard"]="Dashboard en tiempo real"
)

i=0
for name in "${!SEGS[@]}"; do
  img="$PHOTOS_DIR/$name.jpg"
  [ -f "$img" ] || continue
  i=$((i+1))
  txt="${SEGS[$name]}"
  out="$TMP/seg_$i.mp4"
  # zoompan: escala base 1080x1920 recortando, zoom 1.0→1.08
  ffmpeg -y -loop 1 -i "$img" -t 5 -r 30 \
    -vf "scale=2160:3840:force_original_aspect_ratio=increase,crop=2160:3840,zoompan=z='1+0.08*on/(5*30)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s=${W}x${H},scale=${W}:${H},drawtext=text='${txt}':fontfile='${FONT}':fontsize=72:fontcolor=white:x=(w-text_w)/2:y=h-260:shadowcolor=black@0.6:shadowx=4:shadowy=4" \
    -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "$out"
done

# Concat + overlay marca (esquina) + cierre CTA
for f in "$TMP"/seg_*.mp4; do echo "file '$f'"; done > "$TMP/list.txt"
ffmpeg -y -f concat -safe 0 -i "$TMP/list.txt" \
  -vf "drawtext=text='Nathaly · Contabilidad · Hermosillo':fontfile='${FONT}':fontsize=44:fontcolor=white:x=60:y=90:shadowcolor=black@0.6:shadowx=3:shadowy=3" \
  -c:v libx264 -preset medium -crf 23 -pix_fmt yuv420p "$OUT"

echo "✅ Reel generado: $OUT ($(du -h "$OUT" | cut -f1))"
echo "Listo para redes sociales."