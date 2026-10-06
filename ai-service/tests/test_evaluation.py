from fastapi.testclient import TestClient
from app.main import app
from app.services.evaluation_service import EvaluationService

client = TestClient(app)


def test_sweep_measured_values():
    svc = EvaluationService()
    assert svc.size >= 15, "labeled tickets must be loaded"
    result = svc.sweep()

    # The tuned threshold must sit inside the measured safe window.
    assert result["safeWindow"] is not None
    assert result["safeWindow"]["min"] <= result["tunedThreshold"] <= result["safeWindow"]["max"]

    # Separation property measured earlier: min matched > max unmatched.
    assert result["minMatchedScore"] > result["maxUnmatchedScore"]

    # At the tuned threshold: perfect coverage AND refusal accuracy.
    tuned = next(s for s in result["sweep"] if abs(s["threshold"] - 0.15) < 0.001)
    assert tuned["coverage"] == 100.0
    assert tuned["refusalAccuracy"] == 100.0
    assert tuned["falseRefusals"] == 0

    # Monotonicity: coverage never increases with a higher threshold.
    cov = [s["coverage"] for s in result["sweep"]]
    assert all(a >= b for a, b in zip(cov, cov[1:]))

    # Refusal accuracy never decreases with a higher threshold.
    ref = [s["refusalAccuracy"] for s in result["sweep"]]
    assert all(a <= b for a, b in zip(ref, ref[1:]))


def test_evaluate_thresholds_endpoint():
    r = client.get("/ai/evaluate-thresholds")
    assert r.status_code == 200
    d = r.json()
    assert d["dataset"]["tickets"] >= 15
    assert len(d["sweep"]) == 18
    assert 0.05 <= d["tunedThreshold"] <= 0.9
