import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def _upload(csv_text: str, threshold: float = 0.15):
    return client.post(
        "/ai/batch-triage",
        files={"file": ("tickets.csv", io.BytesIO(csv_text.encode("utf-8")), "text/csv")},
        data={"confidenceThreshold": str(threshold)},
    )


def test_batch_tickettext_column():
    csv_text = "ticketId,ticketText\nX-1,User cannot log in account locked after failed login attempts\n"
    r = _upload(csv_text)
    assert r.status_code == 200
    body = r.json()
    assert body["processedRows"] == 1
    row = body["results"][0]
    assert row["decision"] in ("DRAFT_ALLOWED", "NO_RELIABLE_MATCH")


def test_batch_subject_and_body_columns():
    # Regression: the team's multilingual dataset uses subject + body,
    # previously every row was SKIPPED because only ticketText was read.
    csv_text = (
        "subject,body,answer,queue,priority,language\n"
        "Account locked,\"User cannot log in, account locked after too many failed login attempts\",thanks,Technical Support,high,en\n"
        "Nightly batch job failed,\"Batch job failed during the reconciliation step\",ok,IT Support,medium,en\n"
    )
    r = _upload(csv_text)
    assert r.status_code == 200
    body = r.json()
    assert body["totalRows"] == 2
    assert body["skippedRows"] == 0
    decisions = [row["decision"] for row in body["results"]]
    assert "SKIPPED" not in decisions
    assert any(row["topArticleId"] == "KB-01" for row in body["results"])


def test_batch_empty_rows_are_skipped():
    csv_text = 'ticketText\n"   "\n"\t"\n'
    r = _upload(csv_text)
    assert r.status_code == 200
    body = r.json()
    assert body["totalRows"] == 2
    assert body["skippedRows"] == 2
    assert all(row["decision"] == "SKIPPED" for row in body["results"])


def test_batch_non_csv_rejected():
    r = client.post(
        "/ai/batch-triage",
        files={"file": ("data.txt", io.BytesIO(b"hello"), "text/plain")},
        data={"confidenceThreshold": "0.15"},
    )
    assert r.status_code == 400


def test_batch_language_column_respected():
    csv_text = (
        "subject,body,language\n"
        "खाता लॉक,उपयोगकर्ता लॉगिन नहीं कर पा रहा खाता लॉक हो गया,hi\n"
    )
    r = _upload(csv_text)
    assert r.status_code == 200
    row = r.json()["results"][0]
    assert row["language"] == "hi"
