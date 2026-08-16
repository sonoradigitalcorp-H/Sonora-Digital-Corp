#!/usr/bin/env bash
# Wrapper del bot @HermosilloCont_bot (modo polling) — carga ~/.hermes/.env y corre el webhook.
set -a
# shellcheck disable=SC1091
source ~/.hermes/.env
set +a
cd "/home/mystic/Documentos/Sonora Digital Corp Nuevo/02_Client_Projects/Hermosillo_Contabilidad/02_Source_Code" || exit 1
exec python3 telegram_webhook_hermosillo.py --poll