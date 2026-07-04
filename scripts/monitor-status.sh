#!/bin/bash
# SDC Monitor Status — HTML dashboard
echo "Content-Type: text/html"
echo ""
cat << HTML
<html><head><title>SDC Monitor</title>
<style>
body { font-family: monospace; background: #0a0a0f; color: #e0e0e0; padding: 20px; }
h1 { color: #7c3aed; }
.ok { color: #10b981; }
.warn { color: #f59e0b; }
.fail { color: #ef4444; }
.section { border: 1px solid #1a1a2e; padding: 15px; margin: 10px 0; border-radius: 8px; }
</style></head><body>
<h1>🪐 SDC System Monitor</h1>
<p>Updated: $(date '+%Y-%m-%d %H:%M:%S')</p>
<div class="section">
<h2>System</h2>
<pre>$(uptime)
$(free -h | head -2)
$(df -h / | tail -1)</pre>
</div>
<div class="section">
<h2>Docker Containers</h2>
<pre>$(docker ps --format 'table {{.Names}}\t{{.Status}}')</pre>
</div>
<div class="section">
<h2>Cron Logs (last 24h)</h2>
<pre>$(for f in /home/ubuntu/sonora-digital-corp/state/logs/*.log; do echo "$(basename $f): $(wc -l < $f) lines, $(tail -1 $f | cut -c1-80)"; done 2>/dev/null | tail -15)</pre>
</div>
<div class="section">
<h2>Self-Heal Status</h2>
<pre>$(tail -5 /home/ubuntu/sonora-digital-corp/state/logs/events.jsonl 2>/dev/null)</pre>
</div>
</body></html>
HTML
