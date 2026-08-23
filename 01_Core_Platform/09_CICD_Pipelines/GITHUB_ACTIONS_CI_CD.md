# GitHub Actions CI/CD — Sonora Digital Corp (SDC)
**Archivo**: `.github/workflows/ci-cd.yml`

```yaml
name: SDC CI/CD

on:
  push:
    branches: [next, main]
    tags: ['v*']
  pull_request:
    branches: [next]

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  # 1. Lint & Typecheck
  lint:
    name: Lint & Typecheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          pip install -q ruff mypy pytest pyyaml
      - name: Ruff lint
        run: ruff check .
      - name: MyPy typecheck
        run: mypy --ignore-missing-imports 01_Core_Platform/ 03_Sandbox_and_RnD/
      - name: Guardian structure
        run: bash 01_Core_Platform/04_Automations_and_Workflows/structure_guard.sh

  # 2. Unit Tests
  test:
    name: Unit Tests
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: |
          pip install -q pytest pytest-asyncio httpx pyyaml
      - name: Run tests
        run: |
          pytest 03_Sandbox_and_RnD/tests/integration/test_sdd0012_web_chat.py -v
          pytest 03_Sandbox_and_RnD/tests/integration/test_aztrotech_onboard.py -v 2>/dev/null || true

  # 3. Eval Prompts (opcional, requiere OPENROUTER_API_KEY)
  eval-prompts:
    name: Eval Prompts (nemotron-free)
    runs-on: ubuntu-latest
    needs: lint
    if: env.OPENROUTER_API_KEY != ''
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install deps
        run: pip install -q pyyaml
      - name: Run eval
        env:
          OPENROUTER_API_KEY: ${{ secrets.OPENROUTER_API_KEY }}
        run: python3 01_Core_Platform/09_CICD_Pipelines/prompt_registry/run_eval.py
      - name: Upload eval results
        uses: actions/upload-artifact@v4
        with:
          name: eval-results
          path: eval_results.json

  # 4. Build & Push Docker (VPS deploy)
  docker:
    name: Build & Push Docker
    runs-on: ubuntu-latest
    needs: [lint, test]
    if: github.event_name == 'push' && (github.ref == 'refs/heads/next' || startsWith(github.ref, 'refs/tags/v'))
    steps:
      - uses: actions/checkout@v4
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3
      - name: Log in to GHCR
        uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=sha
      - name: Build & Push vps_ai_server
        uses: docker/build-push-action@v5
        with:
          context: 01_Core_Platform/04_Automations_and_Workflows
          file: Dockerfile.vps_ai_server
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
      - name: Build & Push STT Server
        uses: docker/build-push-action@v5
        with:
          context: 01_Core_Platform/03_Agentic_Infrastructure/voice
          file: Dockerfile.stt
          push: true
          tags: ghcr.io/${{ github.repository }}/stt:${{ steps.meta.outputs.tags }}
      - name: Build & Push TTS Server
        uses: docker/build-push-action@v5
        with:
          context: 01_Core_Platform/03_Agentic_Infrastructure/voice
          file: Dockerfile.tts
          push: true
          tags: ghcr.io/${{ github.repository }}/tts:${{ steps.meta.outputs.tags }}

  # 5. Deploy VPS (via SSH)
  deploy-vps:
    name: Deploy VPS OVH
    runs-on: ubuntu-latest
    needs: [docker]
    if: github.event_name == 'push' && github.ref == 'refs/heads/next'
    steps:
      - name: Deploy to VPS
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ubuntu
          key: ${{ secrets.VPS_SSH_KEY }}
          port: 22
          script: |
            set -e
            cd /opt/hermes
            # Pull latest images
            docker compose pull vps_ai_server stt tts
            # Restart services
            docker compose up -d vps_ai_server stt tts
            # Health check
            sleep 5
            curl -f http://localhost:8643/health || exit 1
            curl -f http://localhost:5292/health || exit 1
            curl -f http://localhost:5293/health || exit 1
            echo "✅ VPS deploy OK"

  # 6. Sync Engram (opcional)
  sync-engram:
    name: Sync Engram to VPS
    runs-on: ubuntu-latest
    needs: deploy-vps
    if: github.event_name == 'push' && github.ref == 'refs/heads/next'
    steps:
      - name: Sync Engram
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.VPS_HOST }}
          username: ubuntu
          key: ${{ secrets.VPS_SSH_KEY }}
          port: 22
          script: |
            rsync -avz -e "ssh -i ~/.ssh/id_ed25519_sdc" ~/.engram/ ubuntu@149.56.46.173:~/.engram/

  # 7. Notify
  notify:
    name: Notify Slack/Telegram
    runs-on: ubuntu-latest
    needs: [deploy-vps, sync-engram]
    if: always()
    steps:
      - name: Notify result
        if: success()
        run: |
          echo "✅ SDC v${{ github.ref_name }} deployed to VPS OVH"
      - name: Notify failure
        if: failure()
        run: |
          echo "❌ SDC deploy failed"
```

---

## Secrets Requeridos (GitHub Settings → Secrets)

| Secret | Descripción |
|--------|-------------|
| `OPENROUTER_API_KEY` | Key para eval prompts (opcional) |
| `VPS_HOST` | `149.56.46.173` |
| `VPS_SSH_KEY` | Private key `id_ed25519_sdc` (base64 encoded) |
| `GITHUB_TOKEN` | Auto-provided |

---

## Dockerfiles Necesarios

### `01_Core_Platform/04_Automations_and_Workflows/Dockerfile.vps_ai_server`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY vps_ai_server.py .
RUN pip install --no-cache-dir aiohttp edge-tts
EXPOSE 8643
CMD ["python", "vps_ai_server.py"]
```

### `01_Core_Platform/03_Agentic_Infrastructure/voice/Dockerfile.stt`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY stt_server.py .
RUN pip install --no-cache-dir faster-whisper aiohttp
EXPOSE 5292
CMD ["python", "stt_server.py"]
```

### `01_Core_Platform/03_Agentic_Infrastructure/voice/Dockerfile.tts`
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY tts_server.py .
RUN pip install --no-cache-dir edge-tts aiohttp
EXPOSE 5293
CMD ["python", "tts_server.py"]
```

### `docker-compose.yml` (en `/opt/hermes` en VPS)
```yaml
version: '3.8'
services:
  vps_ai_server:
    image: ghcr.io/sonoradigitalcorp-h/sonora-digital-corp/vps_ai_server:latest
    ports: ["8643:8643"]
    environment:
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
    restart: always

  stt:
    image: ghcr.io/sonoradigitalcorp-h/sonora-digital-corp/stt:latest
    ports: ["5292:5292"]
    environment:
      - STT_MODEL=small
      - STT_COMPUTE=int8
    restart: always

  tts:
    image: ghcr.io/sonoradigitalcorp-H/sonora-digital-corp/tts:latest
    ports: ["5293:5293"]
    restart: always
```

---

## Estructura de Archivos CI/CD

```
.github/
└── workflows/
    └── ci-cd.yml
01_Core_Platform/
├── 04_Automations_and_Workflows/
│   ├── Dockerfile.vps_ai_server
│   └── vps_ai_server.py
└── 03_Agentic_Infrastructure/voice/
    ├── Dockerfile.stt
    ├── Dockerfile.tts
    ├── stt_server.py
    └── tts_server.py
```

---

## Comandos Manuales (si falla Actions)

```bash
# Deploy manual VPS
ssh sdc-prod 'cd /opt/hermes && docker compose pull && docker compose up -d && curl -f http://localhost:8643/health'

# Sync Engram manual
rsync -avz ~/.engram/ ubuntu@149.56.46.173:~/.engram/

# Verificar salud
curl https://sonoradigitalcorp.com/health
```