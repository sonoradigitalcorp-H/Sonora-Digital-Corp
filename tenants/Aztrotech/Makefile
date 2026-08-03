# Aztrotech — Comandos rápidos
# SDC internal use only

.PHONY: help deploy bot-logs vps-health sync-vps

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-15s\033[0m %s\n", $$1, $$2}'

deploy:  ## Rsync tenant aztrotech → VPS
	rsync -avz --delete \
		--exclude='bot/.env' \
		--exclude='__pycache__' \
		--exclude='*.pyc' \
		--exclude='.git' \
		../../sonora-digital-corp/tenants/aztrotech/ \
		ovh:/home/ubuntu/sonora-digital-corp/tenants/aztrotech/
	@echo "✅ Deploy completo. Reinicia el bot con: make restart-bot"

restart-bot:  ## Reiniciar bot de Telegram en VPS
	ssh ovh 'sudo systemctl restart sdc-aztrotech-telegram'
	@echo "✅ Bot reiniciado"

bot-logs:  ## Últimos logs del bot
	ssh ovh 'journalctl -u sdc-aztrotech-telegram --no-pager -n 30'

bot-status:  ## Estado del bot
	ssh ovh 'systemctl status sdc-aztrotech-telegram --no-pager -n 10'

vps-health:  ## Healthcheck VPS
	ssh ovh 'echo "=== DOCKER ===" && docker ps --format "table {{.Names}}\t{{.Status}}" && echo "=== SYSTEMD ===" && systemctl list-units --type=service --state=running | grep -E "openclaw|hermes|sonora|sdc" && echo "=== DISK ===" && df -h / | tail -1'
