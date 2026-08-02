import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from analytics.scorer import score_interaction

def test_good_interaction():
    s = score_interaction("user text", "gracias por la ayuda", True, True, 180)
    assert s >= 70

def test_bad_interaction():
    s = score_interaction("no", "ok", True, False, 5)
    assert s < 50

def test_score_range():
    for _ in range(10):
        s = score_interaction("text", "response", False, False, 60)
        assert 0 <= s <= 100
