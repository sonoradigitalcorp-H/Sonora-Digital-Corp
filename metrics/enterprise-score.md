# Enterprise Score — Sonora Digital Corp

**Version**: 2.0.0 (unified)
**Canonical**: `metrics/enterprise_score.py` (real-time, CLI+API)
**API**: `/api/enterprise-score` delegates to canonical
**Legacy**: v1 webui event-based heuristic and v1 markdown conceptual are retired

---

Every initiative must score ≥ 60 to be approved. 10 real-time metrics, each 0–10 (max 100).

---

## Score Formula

```
Enterprise Score = SUM(metric_score for all 10 metrics) (max 100)
```

| Score | Threshold |
|-------|-----------|
| ≥ 90 | Exceptional — Scale immediately |
| 80–89 | Strong — Approve and fund |
| 70–79 | Good — Approve with monitoring |
| 60–69 | Acceptable — Approve conditionally |
| 40–59 | Weak — Require improvements |
| < 40 | Poor — Kill or reject |

---

## The 10 Real-Time Metrics

| # | Metric | Source | Scoring |
|---|--------|--------|---------|
| 1 | **test_pass_rate** | `pytest tests/ -q` output | ≥99%=10, ≥95%=9, ≥90%=8, ≥80%=7, ≥70%=6, ≥60%=5, else rate/10 |
| 2 | **availability** | TCP socket on webui(5174), abe(5180), hermes(8000), evolution(8080), guardian(8088), content(8765), notebook(8502), omnivoice(3900) | 100%=10, ≥90%=9, ≥80%=8, etc. |
| 3 | **documentation** | `docs/*.md` + product docs | min(10, count/2) |
| 4 | **security** | `state/quality/violations.jsonl` | max(1, 10 - violations) |
| 5 | **automation** | Cron scripts in `scripts/` | min(10, cron_count) |
| 6 | **capabilities** | `capabilities/*/capability.yaml` | min(10, count) |
| 7 | **agents** | `agents/*.yaml` | min(10, count) |
| 8 | **cost_tracking** | `state/economics.db` | 10 if tracked, 5 if not |
| 9 | **services** | Same as availability (backward compat) | Same as availability |
| 10 | **evolution** | Evolution Engine placeholder | Static 8 |

---

## Usage

```bash
# CLI
python3 metrics/enterprise_score.py
python3 metrics/enterprise_score.py --json
python3 metrics/enterprise_score.py --watch   # every 60s

# API (via webui)
GET /api/enterprise-score
```
