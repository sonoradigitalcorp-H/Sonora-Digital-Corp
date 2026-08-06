# SDD 0002: Capa de Conocimiento Exacto (OKF)
## Objetivo
Eliminar alucinaciones con cita: el conocimiento de negocio (tablas, fórmulas,
políticas) se navega como conceptos JSON enteros; el RAG queda solo para memoria experiencial.
## Contrato de retrieve_context(question, tenant)
- Devuelve {corpus: okf|rag|none, concept_id, context}.
- corpus=okf: contexto = concepto completo (tabla intacta). Cita obligatoria del concept_id.
- corpus=rag: contexto marcado como "aproximada, verificar".
- corpus=none: única respuesta permitida al LLM: "no tengo datos verificados".
## Schema de concepto (obligatorio)
id, tenant, name, aliases[], definition, rules[] (R1 sin interpolar, R2 honestidad), tables{}.
## Puerta de calidad
- Evals: el híbrido debe ser >= max(RAG, OKF) en okf_eval_suite.json.
- Integrity tests: schema, valor exacto, aislamiento tenant, contrato none.
## No-objetivos (por ahora)
Judge LLM sobre respuestas finales (siguiente iteración, Camino Cerebro).
