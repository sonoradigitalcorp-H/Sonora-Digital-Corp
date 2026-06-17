"""Tests for the 5 new JARVIS agents (Memory, Explore, Skill, Voice, Review)."""
import pytest
import sys
import os


from core.orchestrator import (
    MemoryAgent,
    ExploreAgent,
    SkillAgent,
    VoiceAgent,
    ReviewAgent,
)


# ===================== MemoryAgent Tests =====================

class TestMemoryAgent:
    @pytest.mark.asyncio
    async def test_store_and_recall(self):
        agent = MemoryAgent()
        store = await agent.run("guardar como test_key_001 es un valor de prueba")
        assert store["status"] == "success"
        assert store["action"] == "stored"

        recall = await agent.run("buscá test_key_001")
        assert recall["status"] == "success"
        assert recall["count"] >= 1

    @pytest.mark.asyncio
    async def test_list_memories(self):
        agent = MemoryAgent()
        result = await agent.run("listá los recuerdos")
        assert result["status"] == "success"
        assert "memories" in result

    @pytest.mark.asyncio
    async def test_forget(self):
        agent = MemoryAgent()
        await agent.run("guardar como forget_test_key este dato se va a borrar")
        forget = await agent.run("olvidate de forget_test_key")
        assert forget["status"] == "success"
        assert forget["action"] == "forgotten"

    @pytest.mark.asyncio
    async def test_recall_shows_memories(self):
        agent = MemoryAgent()
        result = await agent.run("listá los recuerdos")
        assert result["status"] == "success"
        assert "memories" in result


# ===================== ExploreAgent Tests =====================

class TestExploreAgent:
    @pytest.mark.asyncio
    async def test_explore_root(self):
        agent = ExploreAgent()
        result = await agent.run("listá archivos en .")
        assert result["status"] == "success"
        assert len(result["files"]) > 0

    @pytest.mark.asyncio
    async def test_list_src_core(self):
        agent = ExploreAgent()
        result = await agent.run("listá archivos en src/core/")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_structure(self):
        agent = ExploreAgent()
        result = await agent.run("mostrame la estructura del proyecto")
        assert result["status"] == "success"
        assert "tree" in result
        assert len(result["tree"]) > 0

    @pytest.mark.asyncio
    async def test_search_code(self):
        agent = ExploreAgent()
        result = await agent.run('buscá "def test_" en tests/')
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_read_file(self):
        agent = ExploreAgent()
        result = await agent.run("leé el archivo setup.sh")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_explore_nonexistent_path(self):
        agent = ExploreAgent()
        result = await agent.run("listá archivos en /xyz_no_existe_99999")
        assert result["status"] == "success"


# ===================== SkillAgent Tests =====================

class TestSkillAgent:
    @pytest.mark.asyncio
    async def test_list_skills(self):
        agent = SkillAgent()
        result = await agent.run("listá las skills disponibles")
        assert result["status"] == "success"
        assert result["count"] >= 8

    @pytest.mark.asyncio
    async def test_list_skills_default(self):
        agent = SkillAgent()
        result = await agent.run("decime qué skills tenés")
        assert result["status"] == "success"
        assert result["count"] >= 8

    @pytest.mark.asyncio
    async def test_skill_docs(self):
        agent = SkillAgent()
        result = await agent.run("decime cómo funciona web_fetch")
        assert result["status"] == "success"
        assert result["action"] == "docs"

    @pytest.mark.asyncio
    async def test_run_nonexistent_skill(self):
        agent = SkillAgent()
        result = await agent.run("ejecuta una skill que no existe")
        assert result["status"] == "error"


# ===================== VoiceAgent Tests =====================

class TestVoiceAgent:
    @pytest.mark.asyncio
    async def test_status(self):
        agent = VoiceAgent()
        result = await agent.run("estado de voz")
        assert result["status"] == "success"
        assert result["action"] == "status"
        assert "capabilities" in result

    @pytest.mark.asyncio
    async def test_start_session(self):
        agent = VoiceAgent()
        result = await agent.run("iniciá una sesión de voz")
        assert result["status"] == "success"
        assert result["action"] == "session_start"
        assert "session_id" in result

    @pytest.mark.asyncio
    async def test_end_session(self):
        agent = VoiceAgent()
        await agent.run("iniciá una sesión de voz")
        result = await agent.run("corta la comunicacion")
        assert result["status"] == "success"

    @pytest.mark.asyncio
    async def test_speak_offline(self):
        agent = VoiceAgent()
        result = await agent.run("decí Hola mundo")
        assert result["status"] == "success"
        assert result["action"] in ("speak", "speak_offline")


# ===================== ReviewAgent Tests =====================

class TestReviewAgent:
    @pytest.mark.asyncio
    async def test_review_file(self):
        agent = ReviewAgent()
        result = await agent.run("revisá el archivo AGENTS.md")
        assert result["status"] == "success"
        assert "metrics" in result
        assert "score" in result

    @pytest.mark.asyncio
    async def test_review_nonexistent_file(self):
        agent = ReviewAgent()
        result = await agent.run("revisá el archivo no_existe_12345.xyz")
        assert result["status"] == "error"

    @pytest.mark.asyncio
    async def test_review_snippet(self):
        agent = ReviewAgent()
        result = await agent.run("revisá este código: ```python\ndef hola():\n    pass\n```")
        assert result["status"] == "success"
        assert result["action"] == "review_snippet"

    @pytest.mark.asyncio
    async def test_suggest_fixes(self):
        agent = ReviewAgent()
        result = await agent.run("sugerí mejoras para AGENTS.md")
        assert result["status"] == "success"
        assert "suggestions" in result
