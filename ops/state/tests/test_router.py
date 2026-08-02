import pytest
from memory import MemoryRouter, MemoryRef
from memory.stores import WorkingMemory, BusinessMemory, LongMemory, FileMemory


@pytest.fixture
def router():
    r = MemoryRouter()
    r.register("working", WorkingMemory("/tmp/test_memory_working"))
    r.register("business", BusinessMemory("/tmp/test_memory_business"))
    r.register("long", LongMemory())
    r.register("file", FileMemory("/tmp/test_memory_file"))
    return r


@pytest.mark.asyncio
async def test_router_store_and_retrieve(router):
    ref = MemoryRef(type="working", key="test_key", ttl=None)
    result = await router.store(ref, {"hello": "world"})
    assert result.found
    assert result.store_type == "working"

    retrieved = await router.retrieve(ref)
    assert retrieved.found
    assert retrieved.data["hello"] == "world"


@pytest.mark.asyncio
async def test_router_search_all(router):
    ref = MemoryRef(type="working", key="search_test")
    await router.store(ref, {"name": "test_entity"})

    ref2 = MemoryRef(type="business", key="business_test")
    await router.store(ref2, {"revenue": 1000})

    results = await router.search_all("test")
    assert "working" in results
    assert "business" in results


@pytest.mark.asyncio
async def test_router_unknown_type(router):
    ref = MemoryRef(type="semantic", key="unknown")
    result = await router.retrieve(ref)
    assert not result.found
    assert "Unknown" in (result.error or "")


@pytest.mark.asyncio
async def test_router_delete(router):
    ref = MemoryRef(type="working", key="delete_me")
    await router.store(ref, {"data": "to_delete"})
    assert (await router.delete(ref)) is True
    result = await router.retrieve(ref)
    assert not result.found


@pytest.mark.asyncio
async def test_router_list_types(router):
    types = router.list_types()
    assert "working" in types
    assert "business" in types
    assert "long" in types
    assert "file" in types
