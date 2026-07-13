---
name: creator
description: Build and deploy complete agent-native companies. Use when the user asks to create a company, add an artist, or onboard a new tenant.
---

# Creator Skill

Builds complete agent-native companies on SDC. Each company gets:
- Smart app (React/Vite via Open Lovable)
- 6 agents (CEO, Marketing, Content, Sales, Support, Voice)
- Hasura tenant with RLS
- Qdrant knowledge base
- OmniVoice voice cloning (if audio available)
- FAL LoRA training (if photos available)
- Deployed at {name}.sonoracorp.com

## Commands

- `/crear-empresa "Name" --template music-label` — full company
- `/agregar-artista "Name" --tenant abe-music` — add artist to existing tenant

## Pipeline

1. Call `lovable_generate_page` with the company blueprint
2. Create tenant in Hasura via `hasura_mutate`
3. Create 6 agent definition files in `agents/{tenant}/`
4. If photos: call `train_lora` via FAL
5. If audio: call `omnivoice_clone`
6. Configure nginx + systemd → deploy
7. Create Supabase storage folders
8. Save to Engram: `tenant_{name}`
9. Notify via Telegram
