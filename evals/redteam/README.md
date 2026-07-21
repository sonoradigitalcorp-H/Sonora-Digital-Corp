# Red Teaming — SDC LLM Endpoints

## Quick Start

```bash
# Install promptfoo (if not already)
npm install -g promptfoo

# Run red teaming against OpenClaw gateway
promptfoo redteam run -c evals/redteam/redteam.yaml

# View results
promptfoo redteam report
```

## Configuration

Edit `redteam.yaml` to customize:

- `purpose`: Describe what the system must NOT do
- `target`: The endpoint URL and request format
- `plugins`: Attack categories (excessive-agency, pii, harmful:*)
- `strategies`: Delivery methods (prompt-injection, jailbreak, base64, etc.)

## Endpoints

| Endpoint | Port | Purpose |
|----------|------|---------|
| OpenClaw Gateway | 18789 | Skill execution |
| ComfyUI | 8188 | Image generation |
| Hermes SSE | 8000 | Event streaming |

## Notes

- Red teaming generates ~140 attack variants per plugin
- Run against a staging copy first
- Results include: attack payload, response, judge verdict
