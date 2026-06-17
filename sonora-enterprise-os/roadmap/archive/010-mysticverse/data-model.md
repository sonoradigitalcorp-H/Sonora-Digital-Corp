# Data Model: Mysticverse
**Spec**: spec.md
---
## Entidades
| Entidad | Atributos | Descripción |
|---------|-----------|-------------|
| Creator | id, nombre, email, kyc_status | Creador de contenido |
| DigitalTwin | id, creator_id, status, face_trained, voice_cloned, bot_active | Clon digital |
| KycRecord | id, creator_id, document_type, age_verified, identity_verified | Verificación de edad/identidad |
| Player | id, xp, level, streak, badges[] | Jugador con gamificación |
## Relaciones
```
(Creator)-[:TIENE_TWIN]->(DigitalTwin)
(Creator)-[:TIENE_KYC]->(KycRecord)
(Creator)-[:ES_JUGADOR]->(Player)
```
