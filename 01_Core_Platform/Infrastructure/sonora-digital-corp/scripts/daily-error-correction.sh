#!/bin/bash
# Daily Error Correction & Self-Healing
# Runs at 4AM daily via systemd timer (Spec 010)
set -e
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOG="${BASE_DIR}/state/logs/error-correction.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] === JARVIS Error Correction Begin ===" | tee -a $LOG

# 1. Cron: deduplicate
echo "[$DATE] Check cron duplicates..." | tee -a $LOG
crontab -l 2>/dev/null | sort -u | crontab -
echo "[$DATE] Cron: $(crontab -l | wc -l) unique entries" | tee -a $LOG

# 2. n8n: validate all workflow JSON
echo "[$DATE] Validate n8n workflows..." | tee -a $LOG
for f in ${BASE_DIR}/config/n8n*/*.json; do
  python3 -c "import json; json.load(open('$f'))" 2>/dev/null || echo "  BROKEN: $f" >> $LOG
done

# 3. Docker: restart failed containers
echo "[$DATE] Check Docker containers..." | tee -a $LOG
FAILED=$(docker ps -a --filter "status=exited" --format "{{.Names}}" 2>/dev/null)
for c in $FAILED; do
  echo "  Restarting: $c" | tee -a $LOG
  docker start $c 2>/dev/null || echo "  Cannot restart: $c" >> $LOG
done

# 4. Systemd: restart failed services
echo "[$DATE] Check systemd services..." | tee -a $LOG
for s in jarvis-core jarvis-ui sonora-publisher sonora-thumbnails; do
  if ! systemctl is-active --quiet $s 2>/dev/null; then
    echo "  Restarting: $s" | tee -a $LOG
    sudo systemctl restart $s 2>/dev/null || echo "  Cannot restart: $s" >> $LOG
  fi
done

# 5. Disk space check
echo "[$DATE] Disk space..." | tee -a $LOG
USAGE=$(df / | tail -1 | awk '{print $5}' | tr -d '%')
if [ "$USAGE" -gt 85 ]; then
  echo "  WARNING: Disk at ${USAGE}%" | tee -a $LOG
  docker system prune -f 2>/dev/null
fi

# 6. Git sync — SAFE merge (no rebase)
echo "[$DATE] Git sync..." | tee -a $LOG
cd ${BASE_DIR}

# 6a. Check for stuck rebase and abort immediately
if [ -d "$BASE_DIR/.git/rebase-merge" ] || [ -d "$BASE_DIR/.git/rebase-apply" ]; then
  REBASE_AGE=$(stat -c %Y "$BASE_DIR/.git/rebase-merge/head-name" 2>/dev/null || stat -c %Y "$BASE_DIR/.git/rebase-apply/head-name" 2>/dev/null || echo 0)
  NOW=$(date +%s)
  AGE=$((NOW - REBASE_AGE))
  if [ "$AGE" -gt 1800 ]; then  # >30 minutos = stuck
    echo "  ⚠️  Rebase stuck for >30min. Aborting..." | tee -a $LOG
    git rebase --abort 2>/dev/null && echo "  ✅ Rebase aborted." | tee -a $LOG
  else
    echo "  ⚠️  Rebase in progress (${AGE}s). Skipping git sync until rebase is resolved." | tee -a $LOG
    echo "  Run: git rebase --continue (or --abort)" | tee -a $LOG
  fi
fi

# 6b. Check for in-progress merge
if [ -f "$BASE_DIR/.git/MERGE_HEAD" ]; then
  echo "  ⚠️  Merge in progress. Skipping git sync until merge is resolved." | tee -a $LOG
  echo "  Run: git merge --continue (or --abort)" | tee -a $LOG
fi

# 6c. Stash dirty files before sync
DIRTY=$(git status --porcelain 2>/dev/null | wc -l)
if [ "$DIRTY" -gt 0 ]; then
  echo "  Stashing $DIRTY dirty files..." | tee -a $LOG
  git stash push -m "auto-stash before daily sync $(date +%Y-%m-%d)" 2>/dev/null || true
fi

# 6d. Fetch and check divergence
git fetch origin 2>/dev/null
BEHIND=$(git rev-list HEAD..origin/main --count 2>/dev/null)
AHEAD=$(git rev-list origin/main..HEAD --count 2>/dev/null)

if [ "$BEHIND" -gt 0 ] && [ "$AHEAD" -gt 0 ]; then
  # DIVERGENCE — both sides have commits
  echo "  ⚠️  DIVERGENCE: ahead by $AHEAD, behind by $BEHIND commits." | tee -a $LOG
  echo "  Both you and Noel made commits. Merging..." | tee -a $LOG
  git merge origin/main --no-edit 2>/dev/null || {
    echo "  ❌ Merge failed. Manual resolution needed." | tee -a $LOG
    echo "  Run: git merge --abort && scripts/git-sync.sh" | tee -a $LOG
  }
elif [ "$BEHIND" -gt 0 ]; then
  # Only behind — fast-forward (safe)
  echo "  Behind by $BEHIND commits. Fast-forwarding..." | tee -a $LOG
  git merge origin/main --ff-only --no-edit 2>/dev/null || {
    echo "  Fast-forward failed. Trying merge..." | tee -a $LOG
    git merge origin/main --no-edit 2>/dev/null || echo "  ❌ Merge failed." >> $LOG
  }
elif [ "$AHEAD" -gt 0 ]; then
  # Only ahead — push our changes
  echo "  Ahead by $AHEAD commits (not pushed yet)." | tee -a $LOG
  echo "  Will push at end of session (close-session.sh)." | tee -a $LOG
fi

# 6e. Pop stash if we stashed earlier
if [ "$DIRTY" -gt 0 ]; then
  git stash pop 2>/dev/null || echo "  Stash pop failed (keep in stash)." >> $LOG
fi

# 7. Memory save
echo "[$DATE] Memory auto-save..." | tee -a $LOG
python3 ${BASE_DIR}/scripts/automation/memory-save.py 2>/dev/null || echo "  Memory save failed" >> $LOG

# 8. Update DOCUMENTO_DE_ERRORES
echo "[$DATE] Error registry updated" | tee -a $LOG

echo "[$DATE] === JARVIS Error Correction Complete ===" | tee -a $LOG
