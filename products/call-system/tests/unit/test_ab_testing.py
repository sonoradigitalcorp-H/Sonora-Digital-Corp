import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from analytics.ab_testing import assign_variant, register_result, check_optimization

def test_variant_is_valid():
    for _ in range(50):
        v = assign_variant("test", "cold")
        assert v in ("A", "B", "C")

def test_register_result():
    result = register_result("A", 85)
    assert result is None  # Not enough samples yet

def test_optimization_not_triggered_with_few_samples():
    config = {"auto_optimize": True, "min_samples_for_decision": 10, "improvement_threshold": 5}
    variants = {
        "A": {"count": 3, "avg_score": 90, "results": [90] * 3},
        "B": {"count": 3, "avg_score": 50, "results": [50] * 3},
        "C": {"count": 3, "avg_score": 70, "results": [70] * 3},
    }
    config["variants"] = variants
    result = check_optimization(config)
    assert result is None  # Need 10 samples minimum
