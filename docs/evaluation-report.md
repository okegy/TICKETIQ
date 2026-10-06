# 📈 TicketIQ — Evaluation Benchmark Report

- **Evaluated On:** 2026-10-06
- **Test Dataset:** `10 synthetic IT tickets`

## Metrics

| Metric | Value | Target | Status |
|---|---|---|---|
| **Decision Gating Accuracy** | 90.0% | >= 90% | ✅ PASS |
| **Category Classification Accuracy** | 90.0% | >= 85% | ✅ PASS |
| **Step Grounding Verification** | 100% | 100% | ✅ PASS |
| **Refusal of Weak Evidence** | 100% | 100% | ✅ PASS |

## Observations
All ungrounded questions (such as cafeteria hardware or space telemetry) correctly triggered `NO_RELIABLE_MATCH` without hallucinating troubleshooting steps.
