# ABE Music — Recovery Procedure

**Version:** 1.0.0
**Last updated:** 2026-06-24

---

## If the VPS Goes Down

### 1. Re-provision

Create a new Ubuntu VPS (any provider) with minimum 4GB RAM.

### 2. Initial Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essentials
sudo apt install -y nginx certbot python3-certbot-nginx docker.io docker-compose-v2 fail2ban

# Enable firewall
sudo ufw allow 22/tcp && sudo ufw allow 80/tcp && sudo ufw allow 443/tcp && sudo ufw enable
```

### 3. Key Data to Restore

| What | Where to Get It |
|---|---|
| SSH Key | Local: `~/.ssh/id_ed25519_sdc` |
| Telegram Token | `scripts/abe-telegram-bot.py` or `.env` |
| ABE JSON Data | `/home/mystic/sonora-digital-corp/data/abe-music.json` (local) |
| Dashboard HTML | `/home/mystic/sonora-digital-corp/apps/webui/static/abe-command-center.html` (local) |
| Docker Compose | `/home/mystic/sonora-digital-corp/infra/docker-compose-ovh.yml` (local) |

### 4. Copy Files to New Server

```bash
scp -i ~/.ssh/id_ed25519_sdc data/abe-music.json ubuntu@NEW_IP:~/sdc/data/
scp -i ~/.ssh/id_ed25519_sdc apps/webui/static/abe-command-center.html ubuntu@NEW_IP:~/sdc/static/
scp -i ~/.ssh/id_ed25519_sdc scripts/abe-telegram-bot.py ubuntu@NEW_IP:~/sdc/scripts/
```

Copy `abe_server.py` and `docker-compose.yml` from the OVH server or local repo.

### 5. Start Services

```bash
# Docker core services
cd ~/sdc && docker compose up -d

# Systemd services
sudo systemctl enable --now abe-server.service
sudo systemctl enable --now abe-telegram-bot.service
```

### 6. SSL

```bash
sudo certbot --nginx -d sonoradigitalcorp.com -d www.sonoradigitalcorp.com
```

### 7. Update DNS

Point A record `sonoradigitalcorp.com` → new server IP.

---

## If the ABE API Crashes

```bash
sudo systemctl status abe-server.service
sudo systemctl restart abe-server.service
sudo journalctl -u abe-server.service -n 50 --no-pager
```

## If the Telegram Bot Stops

```bash
sudo systemctl status abe-telegram-bot.service
sudo systemctl restart abe-telegram-bot.service
journalctl -u abe-telegram-bot.service -n 50 --no-pager
```

## If the JSON Data Gets Corrupted

The last known good backup is at:

```bash
# Local repo (source of truth)
/home/mystic/sonora-digital-corp/data/abe-music.json

# Git history
cd /home/mystic/sonora-digital-corp && git log --oneline data/abe-music.json
```

## If Docker Containers Fail

```bash
# Check all
docker ps -a

# Restart a single service
docker compose -f ~/sdc/docker-compose.yml up -d --force-recreate <service>

# Full reset
docker compose -f ~/sdc/docker-compose.yml down
docker compose -f ~/sdc/docker-compose.yml up -d
```

## If the Domain/SSL Expires

```bash
# Renew SSL
sudo certbot renew

# Check cert expiry
sudo certbot certificates
```
