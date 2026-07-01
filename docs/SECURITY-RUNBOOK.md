# Security Runbook — Sonora Digital Corp

## 1. VPS Access

| Item | Value |
|------|-------|
| IP | 149.56.46.173 |
| User | ubuntu |
| SSH Key | `~/.ssh/id_ed25519_sdc` |
| Port | 22 |
| Root login | ❌ Disabled |
| Password auth | ❌ Disabled |
| Fail2ban | ✅ Active (sshd + nginx ×3) |

## 2. Firewall (UFW)

```
Status: active
22/tcp  → SSH
80/tcp  → HTTP
443/tcp → HTTPS
Default: deny incoming, allow outgoing
```

## 3. Secrets Management

| Secret | Location | Status |
|--------|----------|--------|
| `.env` file | `~/sonora-digital-corp/.env` | ✅ chmod 600 |
| ABE Telegram token | Env var | ✅ Not in code |
| ABE Fenix token | Env var | ✅ Not in code |
| Mercado Pago token | Env var | ✅ Not in code |
| OpenRouter key | Env var | ✅ Not in code |
| Neo4j password | `.env` + docker-compose | ⚠️ Default in compose |

## 4. Anti-Prompt-Injection

All user-facing endpoints sanitize inputs via `security_guard.py`:
- Blocks: ignore-instructions, you-are-free, DAN, system prompt leaks
- Sanitizes: API keys, JWTs, tokens in responses
- Max input length: 2000 chars

## 5. Docker Security

| Container | Port | Bound To | Status |
|-----------|------|----------|--------|
| postgres | 5432 | 127.0.0.1 | ✅ |
| redis | 6379 | 127.0.0.1 | ✅ |
| neo4j | 7474, 7687 | 127.0.0.1 | ✅ |
| qdrant | 6333, 6334 | 127.0.0.1 | ✅ |
| mcp-server | 8000 | 127.0.0.1 | ⚠️ Unhealthy |
| n8n | 5678 | 127.0.0.1 | ✅ |
| langfuse | 3000 | 127.0.0.1 | ⚠️ Unhealthy |
| telegram-bot | 3003 | 127.0.0.1 | ✅ |
| jarvis-webui | 5174 | 127.0.0.1 | ✅ |

## 6. Monitoring

| System | Status |
|--------|--------|
| Fail2ban | ✅ sshd + nginx-http-auth + nginx-botsearch + nginx-bad-request |
| Crontab healthcheck | Every 15 min (`autonomous.sh`) |
| Git sync | Every hour |
| Disk alert | Every 10 min (>85%) |
| Backup | Daily at 3 AM |

## 7. Incident Response

### If VPS is compromised:
1. Kill SSH session immediately
2. Revoke all API keys in `.env`
3. Rotate GitHub deploy keys
4. Restore from backup: `scripts/volume-backup.sh`
5. Audit `~/.ssh/authorized_keys`
6. Check `~/.bash_history` for unauthorized commands

### If a container is compromised:
1. `docker stop <container>`
2. `docker logs <container> --tail 100`
3. Check container filesystem: `docker diff <container>`
4. Rebuild from clean image: `docker compose build <service>`

### If a service is unhealthy:
1. Check logs: `docker logs <container> --tail 50`
2. Restart: `docker compose restart <service>`
3. If persists, check upstream dependencies

## 8. Recovery from Scratch

```bash
# 1. Provision VPS (Ubuntu 24.04+)
# 2. Install Docker + git
sudo apt update && sudo apt install -y docker.io docker-compose git

# 3. Clone repo
git clone git@github.com:sonoradigitalcorp-H/Sonora-Digital-Corp.git
cd Sonora-Digital-Corp

# 4. Create .env with secrets
cp .env.example .env
# Edit .env with real tokens

# 5. Start everything
docker compose -f infra/docker-compose.yml up -d

# 6. Verify
curl http://localhost:5174/api/enterprise-score
```

## 9. Audit Checklist (for External Auditors)

- [ ] All ports bound to 127.0.0.1 (except 22/80/443)
- [ ] Fail2ban active with ≥4 jails
- [ ] SSH key-only, no passwords
- [ ] `.env` chmod 600
- [ ] No secrets in git history
- [ ] Container memory limits set
- [ ] Docker daemon in user namespace
- [ ] GitHub branch protection active
- [ ] GitHub secret scanning enabled
- [ ] Dependabot configured
- [ ] No stale/unused containers or images
- [ ] Regular backups verified
