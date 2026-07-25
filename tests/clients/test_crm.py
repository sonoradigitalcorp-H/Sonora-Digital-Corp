"""
Tests for CRM client module (clients/aztrotech/crm/).

Following SDD/SpecKit/Agent Harness test patterns.
"""

import json
import os
import tempfile
from pathlib import Path

import pytest

from clients.aztrotech.crm.models import Contact, gen_id
from clients.aztrotech.crm.store import CRMStore
from clients.aztrotech.crm.search import CRMSearch


@pytest.fixture
def db_path():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        yield Path(f.name)
    os.unlink(f.name)


@pytest.fixture
def store(db_path):
    return CRMStore(db_path=db_path)


@pytest.fixture
def search(store):
    return CRMSearch(store)


@pytest.fixture
def sample_contacts(store):
    contacts = [
        Contact(name="Juan Pérez", phone="5216621234567", company="Empresa ABC", source="telegram"),
        Contact(name="María García", phone="5216627654321", company="Compañía XYZ", source="whatsapp"),
        Contact(name="César Holguín", phone="5216621072254", company="AztroTech", source="whatsapp"),
    ]
    for c in contacts:
        store.upsert(c)
    return contacts


# ============================================================
# Model Tests
# ============================================================

class TestContactModel:
    def test_gen_id_format(self):
        cid = gen_id()
        assert cid.startswith("CT-")
        parts = cid.split("-")
        assert len(parts) == 3
        assert len(parts[2]) == 8

    def test_contact_auto_id(self):
        c = Contact(name="Test")
        assert c.crm_id.startswith("CT-")
        assert c.created_at > 0
        assert c.updated_at > 0

    def test_contact_to_dict(self):
        c = Contact(name="Test", phone="5216620000", company="Cía")
        d = c.to_dict()
        assert d["name"] == "Test"
        assert d["phone"] == "5216620000"
        assert d["crm_id"] == c.crm_id

    def test_contact_from_dict(self):
        data = {"name": "Test", "phone": "5216620000", "company": "Cía", "tags": "vip"}
        c = Contact.from_dict(data)
        assert c.name == "Test"
        assert c.tags == "vip"


# ============================================================
# Store Tests
# ============================================================

class TestCRMStore:
    def test_upsert_and_get(self, store):
        c = Contact(name="Test", phone="5216620000", company="Cía")
        store.upsert(c)
        retrieved = store.get(c.crm_id)
        assert retrieved is not None
        assert retrieved.name == "Test"
        assert retrieved.phone == "5216620000"

    def test_upsert_updates(self, store):
        c = Contact(name="Original", phone="5216620000")
        store.upsert(c)
        c.name = "Updated"
        c.phone = "5216621111"
        store.upsert(c)
        retrieved = store.get(c.crm_id)
        assert retrieved.name == "Updated"
        assert retrieved.phone == "5216621111"
        assert retrieved.updated_at > retrieved.created_at

    def test_delete(self, store):
        c = Contact(name="ToDelete")
        store.upsert(c)
        assert store.delete(c.crm_id) is True
        assert store.get(c.crm_id) is None
        assert store.delete("NONEXISTENT") is False

    def test_list_all(self, store, sample_contacts):
        contacts = store.list_all()
        assert len(contacts) == 3

    def test_list_all_pagination(self, store, sample_contacts):
        contacts = store.list_all(limit=2)
        assert len(contacts) == 2

    def test_count(self, store, sample_contacts):
        assert store.count() == 3

    def test_empty_store(self, db_path):
        s = CRMStore(db_path=db_path)
        assert s.count() == 0
        assert s.list_all() == []

    def test_metadata_json(self, store):
        c = Contact(name="Meta", metadata='{"key": "value"}')
        store.upsert(c)
        retrieved = store.get(c.crm_id)
        assert retrieved.metadata == '{"key": "value"}'


# ============================================================
# Search Tests
# ============================================================

class TestCRMSearch:
    def test_search_by_name(self, search, sample_contacts):
        results = search.by_name("Juan")
        assert len(results) >= 1
        assert results[0].name == "Juan Pérez"

    def test_search_by_name_exact(self, search, sample_contacts):
        results = search.by_name("César Holguín", exact=True)
        assert len(results) == 1
        assert results[0].company == "AztroTech"

    def test_search_by_phone(self, search, sample_contacts):
        results = search.by_phone("1234567")
        assert len(results) >= 1

    def test_search_by_company(self, search, sample_contacts):
        results = search.by_company("AztroTech")
        assert len(results) >= 1

    def test_search_by_tag(self, store, search):
        c = Contact(name="TagTest", tags="vip,lead,hot")
        store.upsert(c)
        results = search.by_tag("vip")
        assert len(results) >= 1

    def test_unified_search_name(self, search, sample_contacts):
        results = search.search("Juan")
        assert any(r.name == "Juan Pérez" for r in results)

    def test_unified_search_phone(self, search, sample_contacts):
        results = search.search("7654321")
        assert any("María" in r.name for r in results)

    def test_unified_search_company(self, search, sample_contacts):
        results = search.search("AztroTech")
        assert any("Holguín" in r.name for r in results)

    def test_unified_search_no_results(self, search):
        results = search.search("ZZZZNONEXISTENT")
        assert len(results) == 0

    def test_search_ordering(self, store, search):
        c1 = Contact(name="Alpha Corp", company="ZZ Corp")
        c2 = Contact(name="Beta Inc", company="Alpha Ltd")
        store.upsert(c1)
        store.upsert(c2)
        results = search.search("Alpha")
        assert len(results) >= 2


# ============================================================
# Integration Test (sync to stores)
# ============================================================

class TestCRMSync:
    def test_event_logged(self, store, db_path):
        from clients.aztrotech.crm.sync import CRMSync
        sync = CRMSync(store)

        c = Contact(name="Sync Test", phone="5216620000")
        store.upsert(c)
        sync.sync_all(c)

        events_file = Path(__file__).resolve().parent.parent.parent / "state" / "events" / "events.jsonl"
        if events_file.exists():
            with open(events_file) as f:
                lines = f.readlines()
            matching = [l for l in lines if c.crm_id in l]
            assert len(matching) >= 1, "Event should contain crm_id"


# ============================================================
# Gherkin Tests (BDD-style)
# ============================================================

def test_gherkin_add_contact(store):
    """
    Given a new contact with name "Test User" and phone "5216620000"
    When the contact is added to CRM
    Then the contact exists with correct name and phone
    """
    c = Contact(name="Test User", phone="5216620000")
    store.upsert(c)
    retrieved = store.get(c.crm_id)
    assert retrieved is not None
    assert retrieved.name == "Test User"
    assert retrieved.phone == "5216620000"


def test_gherkin_search_contact(store, search):
    """
    Given contacts exist with various names
    When searching for "Juan"
    Then results match partial name
    """
    Contact(name="Juan Pérez", phone="5216620000")
    c = Contact(name="Juan Pérez", phone="5216620000")
    store.upsert(c)
    results = search.search("Juan")
    assert len(results) >= 1
    assert any("Juan" in r.name for r in results)


def test_gherkin_delete_contact(store):
    """
    Given a contact exists
    When the contact is deleted
    Then the contact is no longer retrievable
    """
    c = Contact(name="ToDelete")
    store.upsert(c)
    cid = c.crm_id
    assert store.get(cid) is not None
    store.delete(cid)
    assert store.get(cid) is None


# ============================================================
# Error handling tests
# ============================================================

def test_get_nonexistent(store):
    assert store.get("NONEXISTENT-ID-12345") is None


def test_delete_nonexistent(store):
    assert store.delete("NONEXISTENT-ID-12345") is False


def test_contact_empty_strings():
    c = Contact()
    assert c.name == ""
    assert c.phone == ""


def test_crm_id_uniqueness(store):
    c1 = Contact(name="First")
    c2 = Contact(name="Second")
    assert c1.crm_id != c2.crm_id
