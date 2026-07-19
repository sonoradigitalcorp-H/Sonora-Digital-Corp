# skills/nsfw — Adult Content Generation with Safety Controls

**Inherits**: OMEGA PROMPT v10.0 + SOUL.md
**Template Version**: 1.0.0
**Audit ID**: SKILL-NSF-001

---

## 1. Business Objective

Generate and manage adult content through controlled pipelines with comprehensive safety guardrails — age-gating, consent verification, content classification, tenant isolation, and full audit trails.

## 2. Inputs (Gherkin)

```gherkin
Given a tenant has NSFW generation enabled in their policy config
And age verification has passed for the requesting user
And consent is registered for all subjects in the generation request
When a generation request includes prompt, style, and policy parameters
```

## 3. Outputs (Gherkin)

```gherkin
Then the content is generated using the configured model (image, text, or voice)
And the output is classified (safe/suggestive/explicit/extreme)
And the content is watermarked with generation metadata
And the generation is logged to the audit trail
And if policy violations are detected, the content is blocked
```

## 4. Events

```
Events:
- nsfw:content:generated: adult content was produced and stored
- nsfw:safety:triggered: a safety policy blocked a generation
- nsfw:consent:added: a subject's consent was registered
- nsfw:consent:revoked: a subject's consent was revoked
```

## 5. Dependencies

```
Dependencies:
- FAL AI: service — image/video generation (SDXL, Flux, LoRA NSFW models)
- OmniVoice: service — voice cloning for adult audio
- OpenRouter: service — text generation (Mythomax, etc.)
- Hasura: service — audit log and consent registry storage
- Supabase storage: service — content storage with access control
- Engram: service — consent registry persistence
```

## 6. Tools

```
Tools:
- llm_chat: generate adult narratives and scripts
- generate_video: generate animated adult content
- gen_photo: generate NSFW images via FAL AI
- upload_file: store generated content with access controls
```

## 7. Policies

```
Policies:
- NEVER generate NSFW content without explicit subject consent
- ALWAYS check age gate (18+ mandatory) before serving content
- ALWAYS watermark AI-generated adult content with generation metadata
- LOG every generation with user_id, prompt, model, and timestamp
- HONOR opt-out registry on every generation request
- BLOCK illegal content (underage, non-consensual, prohibited categories)
- TENANT isolation: NSFW data must not leak across tenants
- ENFORCE jurisdiction-based rules (US, EU, JP, etc.)
- DEFAULT to strict policy; tenants may moderate to permissive
```

## 8. Success Metrics

```gherkin
Success Metrics:
- generation_time: Given valid request When content generated Then seconds
  Target: < 30 sec
- policy_compliance: Given generations audited When checked Then no violations detected
  Target: 100%
- consent_coverage: Given subjects in generation When verified Then consent registered
  Target: 100%
```

## 9. Failure Conditions

```
Failure Conditions:
- Consent not found: subject missing from consent registry (detect via registry lookup)
- Age gate failure: user age verification expired or invalid (detect via session check)
- Model safety bypass: generated content bypasses classification (detect via multi-model voting)
- Jurisdiction mismatch: content violates local laws (detect via geo-IP + policy matrix)
- Audit log gap: generation not recorded (detect via log count vs generation count)
```

## 10. Recovery Procedure

```
Recovery Procedure:
1. If consent missing → block generation, notify user to register consent
2. If age gate expired → request re-verification, block until complete
3. If model bypasses safety → flag for manual review, add to blocklist
4. If jurisdiction error → apply most restrictive rule, log for compliance review
5. If audit log missing → retry write, escalate if persistent
6. Log all safety events to state/logs/skills/nsfw.log
```

## 11. Business Value

```
Business Value: Enables compliant adult content vertical with full safety and audit controls.
```

## 12. Parent OS

```
Parent OS: Security
```

## 13. Version

```
Version: 1.0.0
```

## 14. Audit Trail

```
Audit Trail:
- ADR: ADR-2026-NSF-001
- Events: nsfw:content:generated, nsfw:safety:triggered, nsfw:consent:added, nsfw:consent:revoked
- Logs: state/logs/skills/nsfw.log
```
