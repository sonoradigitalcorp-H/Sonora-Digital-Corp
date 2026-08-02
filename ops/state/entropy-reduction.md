# Quarterly Entropy Reduction

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Version**: 1.0.0
**Audit ID**: METRICS-ENTROPY-001
**Frequency**: Every quarter (last week of Mar, Jun, Sep, Dec)

---

## Checklist

### 1. Remove Unnecessary Tools

- [ ] Review all Docker containers — any that can be stopped?
- [ ] Review all npm packages — any unused?
- [ ] Review all Python packages — any unused?
- [ ] Review all GitHub Actions workflows — any stale?
- [ ] Review all cron jobs — any that fail or are redundant?

### 2. Remove Unnecessary Agents

- [ ] Review all systemd services — any that can be stopped?
- [ ] Review all Docker services — any that duplicate systemd?
- [ ] Review agent registry (agents/MANIFEST.md) — any stale?

### 3. Remove Unnecessary Workflows

- [ ] Review n8n workflows — any not used in 90d?
- [ ] Review GitHub Actions — any failing consistently?
- [ ] Review cron jobs — any with errors in logs?

### 4. Remove Duplicate Systems

- [ ] Check for split-brain services (systemd + Docker same service)
- [ ] Check for duplicate event producers
- [ ] Check for duplicate data stores

### 5. Remove Obsolete Capabilities

- [ ] Review all skills — any never called?
- [ ] Review all harnesses — any with zero usage?
- [ ] Review all initiatives — any that should be killed?

### 6. Reduce Complexity

- [ ] Count total components and compare to last quarter
- [ ] Identify top 5 most complex components
- [ ] Simplify each by ≥20%

### 7. Increase Resilience

- [ ] Test backup restore procedure
- [ ] Run recovery drill (simulate container failure)
- [ ] Verify all healthchecks pass
- [ ] Verify all events flow correctly

---

## Score Calculation

| Area | Weight | Score (0-10) |
|------|--------|--------------|
| Tools removed | 15% | |
| Agents removed | 15% | |
| Workflows removed | 15% | |
| Duplicates resolved | 20% | |
| Complexity reduced | 15% | |
| Resilience improved | 20% | |

**Target**: ≥ 8/10 weighted score

---

## Automation

Run with: `bash scripts/entropy-reduction.sh`

Output: `state/logs/entropy-{YYYY-Q1|Q2|Q3|Q4}.json`

Event: `entropy_reduction_completed`
