# Recovery Manual — Sonora Digital Corp

## Complete System Recovery

### 1. Total VPS Failure (VPS dies)
```
1. Provision new VPS at OVH (or any provider)
2. Install: sudo apt install -y docker.io git
3. Clone: git clone git@github.com:sonoradigitalcorp-H/Sonora-Digital-Corp.git
4. .env: cp .env.example .env (paste secrets from password manager)
5. Start: cd Sonora-Digital-Corp && docker compose -f infra/docker-compose.yml up -d
6. Verify: curl http://localhost:5174/api/enterprise-score
7. Restore volumes from backup: bash scripts/volume-backup.sh restore
8. Restart: docker compose -f infra/docker-compose.yml restart
```

### 2. Docker Daemon Failure
```
sudo systemctl restart docker
docker compose -f infra/docker-compose.yml up -d
```

### 3. Single Container Failure
```
# Check logs
docker logs <container> --tail 50

# Restart
docker compose -f infra/docker-compose.yml restart <service>

# Rebuild if needed
docker compose -f infra/docker-compose.yml build <service>
docker compose -f infra/docker-compose.yml up -d <service>
```

### 4. Database Corruption (Neo4j)
```
docker compose -f infra/docker-compose.yml stop neo4j
docker compose -f infra/docker-compose.yml rm neo4j
# Restore from backup
docker compose -f infra/docker-compose.yml up -d neo4j
```

### 5. SSL Certificate Failure
```
sudo certbot renew --force-renewal
sudo nginx -t && sudo systemctl reload nginx
```

### 6. Secrets Leak (token exposed)
```
1. Revoke token immediately (BotFather, Mercado Pago, etc.)
2. Generate new token
3. Update .env on VPS
4. docker compose -f infra/docker-compose.yml restart
5. Check git history for exposed tokens
6. If in git: gh secret delete <name> && force rotate
```

### 7. Git Corruption / Branch Issues
```
git fetch origin
git reset --hard origin/main
```

### 8. Emergency Stop (all services)
```
docker compose -f infra/docker-compose.yml down
sudo systemctl stop nginx
sudo ufw deny 80 443
```

### Quick Reference
```bash
# Logs
docker logs sdc-jarvis-webui --tail 50
docker logs sdc-jarvis-core --tail 50
docker logs sdc-neo4j --tail 50

# Restart all
docker compose -f infra/docker-compose.yml restart

# Full rebuild
docker compose -f infra/docker-compose.yml build --no-cache
docker compose -f infra/docker-compose.yml up -d

# Backup
bash scripts/volume-backup.sh

# Health check
bash scripts/agents-survey.sh
```
