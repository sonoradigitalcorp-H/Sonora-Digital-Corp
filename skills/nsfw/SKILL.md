---
name: nsfw
description: Generate and manage adult content pipelines with safety controls. Use when the user asks to create, filter, or moderate NSFW/adult content, or when building adult-content agents.
version: 1.0.0
updated: 2026-07-14
---

# NSFW Skill

Generates adult/NSFW content through controlled pipelines with safety guardrails, consent verification, and age-gating.

## Capabilities

### Content Generation
- Text-to-image NSFW generation via FAL/Stable Diffusion (uncensored models)
- Adult storytelling / erotic narrative generation
- Voice content (intimate ASMR, erotic audio via OmniVoice)
- Character/avatar NSFW variants (LoRA, fine-tuned models)
- Video generation (animated adult content)

### Safety & Compliance Controls
- Age verification gate (18+ mandatory)
- Consent model: verify subject consent before generating
- Content watermarking for AI-generated adult content
- Opt-out registry for artists/subjects
- Jurisdiction-based content rules (US, EU, JP, etc.)

### Moderation
- Classification: safe / suggestive / explicit / extreme
- Automatic blur/block based on tenant policy
- Report + appeal workflow for false positives
- Audit log of all NSFW generations (who, what, when)

## Configuration

```yaml
nsfw:
  enabled: true
  default_policy: strict  # strict | moderate | permissive
  age_gate: true
  jurisdictions:
    - US
    - EU
  consent_required: true
  watermark: true
  models:
    image: fal-ai/flux-schnell-nsfw
    text: openrouter/mythomax-l2-13b
    voice: omnivoice-clone
```

## Commands

- `/nsfw generate "prompt" --style realistic --policy moderate` — generate NSFW content
- `/nsfw moderate <url|text>` — classify content as safe/suggestive/explicit
- `/nsfw config --policy strict` — update NSFW policy
- `/nsfw consent add <subject>` — register consent
- `/nsfw consent remove <subject>` — revoke consent

## Tools Used

- `fal_ai` — image/video generation (SDXL, Flux, LoRA)
- `omnivoice_clone` — voice cloning for adult audio
- `hasura_mutate` — store audit log in Hasura
- `supabase_storage` — store generated content with access control
- `engram_save` — persist consent registry

## Policies

1. NEVER generate NSFW content without explicit user consent
2. ALWAYS check age gate before serving content
3. ALWAYS watermark AI-generated adult content
4. LOG every generation with user_id, prompt, model, timestamp
5. HONOR opt-out registry on every generation
6. BLOCK illegal content (underage, non-consensual, prohibited categories)
7. TENANT isolation: NSFW data must not leak across tenants
