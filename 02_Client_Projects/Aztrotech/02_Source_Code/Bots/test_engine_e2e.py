"""Prueba end-to-end del ConversationEngine con router real."""
import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


async def main():
    from conversation_engine import create_engine, EngineConfig
    from router import ModelRouter
    import yaml

    with open(os.path.join(os.path.dirname(__file__), "..", "config.yaml")) as f:
        config = yaml.safe_load(f)
    config["openrouter"]["api_key"] = os.getenv("OPENROUTER_API_KEY")
    router = ModelRouter(config)

    eng = create_engine(EngineConfig(tenant_id="aztrotech"))
    await eng.start()

    internal_id = await eng.resolve_user("telegram", "123456789", {"display_name": "Prueba"})
    print(f"internal_id: {internal_id}")

    casos = [
        "¿Cuánto cuesta el empleado digital?",
        "Hola, me interesa automatizar mi negocio, soy el dueño de una taquería en Culiacán.",
        "Precio no importa, necesito lanzar YA, tengo el dinero listo.",
    ]
    for msg in casos:
        r = await eng.process(
            msg,
            internal_id,
            "telegram",
            f"tg:123456789",
            history=[],
            router=router,
        )
        print("\n" + "=" * 60)
        print(f"MSG: {msg}")
        print(f"REPLY: {r.reply[:200]}")
        print(f"LEAD: {r.lead_type} ({round(r.lead_confidence*100)}%)  EMO: {r.dominant_emotion}")
        print(f"RAG chunks: {r.rag_chunks} | model: {r.model} | cost: ${r.cost_usd:.6f}")
        print(f"guardrail_pass: {r.guardrail_pass} {r.guardrail_note}")

    await eng.stop()


asyncio.run(main())
