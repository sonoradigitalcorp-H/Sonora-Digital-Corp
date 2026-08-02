import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from tenant.service import create_tenant, get_tenant, get_lead_type

def test_create_and_retrieve():
    t = create_tenant("Test User", "+52123456789", "Test Corp")
    assert t["name"] == "Test User"
    assert t["phone"] == "+52123456789"
    assert t["plan"] == "trial"

    found = get_tenant(phone="+52123456789")
    assert found is not None
    assert found["name"] == "Test User"

def test_get_lead_type_new():
    t = create_tenant("New Lead", "", "New Co")
    assert get_lead_type(t) == "cold"

def test_get_lead_type_warm():
    t = create_tenant("Warm Lead", "", "Warm Co")
    t["total_calls"] = 3
    t["plan"] = "trial"
    assert get_lead_type(t) == "warm"

def test_get_lead_type_hot():
    t = create_tenant("Hot Client", "", "Hot Co")
    t["tier"] = "enterprise"
    assert get_lead_type(t) == "hot"
