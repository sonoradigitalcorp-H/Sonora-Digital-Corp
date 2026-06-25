# Pre-Action Intelligence Checklist
_Read at session boot. Check relevant sections before acting._

## HOW TO USE THIS SYSTEM
- **Before risky actions:** Check the relevant section below
- **After mistakes or debugging:** Append an event to `memory/learning/events.jsonl`
- **After proven lessons:** Add/update rules in `memory/learning/rules.json`
- **Event format:** `{"ts":"ISO","type":"mistake|success|debug_session","category":"...","tags":[...],"problem":"...","solution":"...","confidence":"testing|proven","source":"..."}`

## Account / Credential Operations
Before creating or authenticating ANY account:
1. Search your memory files for the service name
2. Check your credential manager for existing entries
3. Check existing cron jobs or config for API keys
**If ANY source shows existing account, STOP.**

## Shell Commands
- Test commands on small inputs first before running on large datasets
- Save working commands to your events log for reuse
- When a command fails, log the error and solution

## External Communications
- Verify recipient before sending
- Double-check content for accuracy
- Log what was sent for future reference

## Rule Confidence Decay (v1.4.0)
Rules lose confidence over time if not validated:
- Check `confidence_score` in rules.json before relying on old rules
- Rules with confidence < 0.5 are flagged for review
- Run `bash confidence-decay.sh` weekly to update scores

## Cross-Agent Rule Sharing (v1.4.0)
- Export rules: `bash export-rules.sh --output rules-export.json`
- Import rules: `bash import-rules.sh rules-export.json`
- Conflicts are detected automatically during import
