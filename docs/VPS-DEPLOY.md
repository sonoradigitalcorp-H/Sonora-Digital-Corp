# VPS Deploy — Live Data Pipeline

SSH access required. Key: `~/.ssh/id_ed25519_sdc` or the key you have access to.

```bash
# 1. Sync scrapers
rsync -avz --delete scrapers/ ubuntu@149.56.46.173:~/sdc/scrapers/

# 2. Deploy Docker scrapers
ssh ubuntu@149.56.46.173 "cd ~/sdc/scrapers && docker compose -f docker-compose.scrapers.yml up -d"

# 3. Healthcheck
ssh ubuntu@149.56.46.173 "curl -s http://localhost:3000/health && echo ' crw OK'"
ssh ubuntu@149.56.46.173 "curl -s http://localhost:8931/health && echo ' playwright OK'"

# 4. First sync
ssh ubuntu@149.56.46.173 "cd ~/sdc && python3 -m scrapers.sync"

# 5. Install cron (every 6h)
ssh ubuntu@149.56.46.173 "cd ~/sdc && bash scripts/install-sync-cron.sh"
```
