# Sonora Digital Corp — Mobile Apps

## Stack: React Native (Expo) + FastAPI backend

### Apps to build:
1. **SDC Connect** — Client portal: chatbots, store, automation dashboard
2. **Brand Studio** — White-label branding tool for clients (Alejandro Zamora)
3. **Content Engine** — YouTube + social media automation manager

### Architecture:
```
React Native (Expo) → FastAPI → n8n → Docker services
                    → WebSocket for real-time chat
                    → Neo4j for personalized memory
```

### Design system:
- Colors: Gold (#FFD700) + Black (#0A0A0A) + White
- Typography: Inter, monospace for code
- Components: Bottom tabs, cards, chat bubbles, metric widgets
