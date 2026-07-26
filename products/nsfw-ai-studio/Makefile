.PHONY: up down restart logs ps pull clean train setup-models generate-video lipsync help

SHELL := /bin/bash

include .env
export $(shell sed 's/=.*//' .env)

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# === Gestión del stack ===

up: ## Levanta todos los servicios
	docker compose up -d

down: ## Detiene todos los servicios
	docker compose down

restart: down up ## Reinicia todo

logs: ## Sigue logs de todos los servicios
	docker compose logs -f

ps: ## Estado de los servicios
	docker compose ps

pull: ## Actualiza imágenes
	docker compose pull

clean: ## Limpia volúmenes y caché
	docker compose down -v
	docker system prune -f

# === ComfyUI ===

comfyui-shell: ## Shell dentro de ComfyUI
	docker exec -it nsfw-comfyui bash

comfyui-logs: ## Logs de ComfyUI
	docker compose logs -f comfyui

# === Entrenamiento ===

train-lora: ## Entrena un LoRA (usa: make train-lora CONFIG=configs/lora-training.yaml)
	@echo "=== Iniciando entrenamiento LoRA ==="
	@docker exec nsfw-kohya bash -c "cd /workspace && accelerate launch --num_cpu_threads_per_process 2 kohya_ss/sdxl_train_network.py --config config/$(or $(CONFIG),lora-training.yaml)"
	@echo "=== Entrenamiento completado ==="
	@echo "Output: $(OUTPUT_DIR)/loras/"

train-lora-aitk: ## Entrena con AI Toolkit (make train-lora-aitk CONFIG=configs/lora-training.yaml)
	@echo "=== Iniciando entrenamiento con AI Toolkit ==="
	@docker exec nsfw-aitoolkit bash -c "cd /app/ai-toolkit && python run.py --config config/$(or $(CONFIG),lora-training.yaml)"
	@echo "=== Entrenamiento completado ==="

# === Generación de video ===

generate-video: ## Genera video desde workflow (make generate-video WORKFLOW=workflow.json)
	@echo "=== Generando video ==="
	@./scripts/generate-video.sh $(WORKFLOW)
	@echo "=== Video generado: $(OUTPUT_DIR)/ ==="

# === Lip Sync ===

lipsync: ## Sincroniza labios con audio
	@echo "=== Sincronizando lip-sync ==="
	@./scripts/sync-lips.sh

# === Pipeline completo ===

auto-pipeline: ## Pipeline completo: entrenar LoRA -> generar video -> lip-sync
	@echo "========================================"
	@echo "  PIPELINE AUTOMÁTICO NSFW AI STUDIO"
	@echo "========================================"
	@./scripts/auto-pipeline.sh

# === Setup ===

setup-models: ## Descarga modelos base
	@echo "=== Descargando modelos base ==="
	@./scripts/setup-models.sh

setup: setup-models up ## Setup completo

# === Utilidades ===

shell-kohya: ## Shell en contenedor Kohya
	docker exec -it nsfw-kohya bash

shell-comfyui: ## Shell en ComfyUI
	docker exec -it nsfw-comfyui bash
