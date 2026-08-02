# Social Media Automation Skill

## Overview
Automate social media posting, responses, and engagement for Sonora Digital Corp using Playwright.

## Tools Available
- `social_post` — Post content to Twitter/Instagram
- `social_schedule` — Generate and schedule content
- `social_queue` — Check content queue status
- `social_generate` — Generate content from topics
- `social_response` — Generate responses for mentions/DMs
- `social_status` — Full system status
- `social_memory_check` — Check memory/RAM usage

## Anti-Loop Protections
- Max 512MB RAM usage
- Auto-restart browser every 30 minutes
- Rate limit: 10 actions/hour per platform
- Cooldown: 2 minutes between actions
- Max 100 iterations per session
- Max 5 same actions in a row

## Usage

### Generate Content
```
Use social_generate with platform="twitter", count=5
```

### Post Content
```
Use social_post with platform="twitter", text="My tweet text"
```

### Schedule Posts
```
Use social_schedule with platform="twitter", count=5
```

### Check Status
```
Use social_status
```

### Generate Response
```
Use social_response with platform="twitter", context="mentions", username="amigo"
```

## Memory Protection
Before each action, the system checks:
1. RAM usage < 512MB
2. Actions this hour < 10
3. Time since last action > 2 minutes
4. Total iterations < 100
5. Same action repeated < 5 times

If any check fails, the action is blocked and logged.

## Cookie/Session Management
- Sessions stored in SQLite (not JSON files)
- Auto-restore on restart
- 7-day log retention
- Cleanup on shutdown