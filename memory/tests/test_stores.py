import shutil
import tempfile

import pytest

from memory.stores import WorkingMemory, BusinessMemory, FileMemory, LongMemory, EventMemory


@pytest.fixture
def tmp_dir():
    d = tempfile.mkdtemp()
    yield d
    shutil.rmtree(d)


@pytest.mark.asyncio
async def test_working_store_roundtrip(tmp_dir):
    store = WorkingMemory(tmp_dir)
    result = await store.store("key1", {"value": 42})
    assert result.found

    retrieved = await store.retrieve("key1")
    assert retrieved.found
    assert retrieved.data["value"] == 42


@pytest.mark.asyncio
async def test_working_store_miss(tmp_dir):
    store = WorkingMemory(tmp_dir)
    result = await store.retrieve("nonexistent")
    assert not result.found


@pytest.mark.asyncio
async def test_working_store_delete(tmp_dir):
    store = WorkingMemory(tmp_dir)
    await store.store("del_key", {"x": 1})
    assert await store.delete("del_key") is True
    result = await store.retrieve("del_key")
    assert not result.found


@pytest.mark.asyncio
async def test_working_store_search(tmp_dir):
    store = WorkingMemory(tmp_dir)
    await store.store("alpha", {"name": "alpha entity"})
    await store.store("beta", {"name": "beta entity"})

    results = await store.search("alpha")
    assert len(results) >= 1
    assert results[0].key == "alpha"


@pytest.mark.asyncio
async def test_working_store_list_keys(tmp_dir):
    store = WorkingMemory(tmp_dir)
    await store.store("abc", {})
    await store.store("abd", {})
    await store.store("xyz", {})

    keys = await store.list_keys("ab")
    assert len(keys) == 2


@pytest.mark.asyncio
async def test_business_store_roundtrip(tmp_dir):
    store = BusinessMemory(tmp_dir)
    result = await store.store("contract_1", {"artist": "Hector", "revenue": 460372})
    assert result.found

    retrieved = await store.retrieve("contract_1")
    assert retrieved.found
    assert retrieved.data["artist"] == "Hector"


@pytest.mark.asyncio
async def test_file_store(tmp_dir):
    store = FileMemory(tmp_dir)
    result = await store.store("hello.txt", {"content": "Hello World"})
    assert result.found

    retrieved = await store.retrieve("hello.txt")
    assert retrieved.found
    assert "Hello World" in retrieved.data.get("content", "")


@pytest.mark.asyncio
async def test_event_store(tmp_dir):
    store = EventMemory(f"{tmp_dir}/events.jsonl")
    result = await store.store("evt1", {"type": "test"})
    assert result.found

    retrieved = await store.retrieve("evt1")
    assert retrieved.found


@pytest.mark.asyncio
async def test_long_store_in_memory(tmp_dir):
    store = LongMemory(f"{tmp_dir}/nonexistent.db")
    result = await store.store("lesson_1", {"text": "Always test"})
    assert result.found

    retrieved = await store.retrieve("lesson_1")
    assert retrieved.found
    assert retrieved.data["text"] == "Always test"


@pytest.mark.asyncio
async def test_long_store_ttl(tmp_dir):
    store = LongMemory(f"{tmp_dir}/nonexistent.db")
    await store.store("ttl_test", {"data": "expired"})
    keys = await store.list_keys("ttl")
    assert "ttl_test" in keys
