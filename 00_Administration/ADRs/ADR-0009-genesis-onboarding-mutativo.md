# ADR-0009: GENESIS — onboarding mutativo de clientes
Estado: ACEPTADO 2026-08-17
Contexto: El onboarding debe vender, preparar lo que cada cliente necesita y
   auto-mejorarse, sin intervención humana y sin caos.
Decisión:
1. GENESIS (PROMPT 0) corre como cronjob NATIVO de Hermes. Nunca proceso aparte.
2. Emite 4 prompts versionados por tenant: P-ONBOARD (vende: propone, no
   pregunta + visual FAL + cierre demo), P-PREPARE (landing estática sin build +
   cotización OKF + 1 canal), P-CAMPAIGN (rate limits humanos), P-REPORT (voz al jefe).
3. Mutación = vN+1 con historial en 00_Administration/Prompt_Registry/mutations/.
   Fallo de VERIFY = rollback automático a vN-1 + lección Engram.
4. Segundo canal por tenant solo tras 72h estable del primero.
5. Máx 3 assets/día por tenant sin aprobación.
Consecuencias: cada ciclo deja lección Engram; el sistema se mejora solo
pero versionado y con rollback.