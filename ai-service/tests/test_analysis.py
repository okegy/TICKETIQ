from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "TicketIQ AI"}

def test_analyze_ticket_success():
    payload = {
        "ticketId": "INC-1001",
        "ticketText": "Payroll portal login failing with AUTH-401 error after password reset for user john.doe@example.com",
        "confidenceThreshold": 0.1
    }
    response = client.post("/ai/analyze-ticket", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "DRAFT_ALLOWED"
    assert "[REDACTED_EMAIL]" in data["redactedText"]
    assert len(data["resolutionSteps"]) > 0
    assert data["classification"]["category"] == "Access Management"

def test_analyze_ticket_no_match():
    payload = {
        "ticketId": "INC-9999",
        "ticketText": "Quantum computing satellite array failure",
        "confidenceThreshold": 0.5
    }
    response = client.post("/ai/analyze-ticket", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "NO_RELIABLE_MATCH"

def test_find_duplicates():
    payload = {
        "ticketText": "GlobalProtect VPN timeout ERR_GATEWAY_UNREACHABLE on laptop",
        "historicalTickets": [
            {
                "id": "INC-100",
                "title": "VPN issue",
                "rawDescription": "GlobalProtect VPN connection failed with ERR_GATEWAY_UNREACHABLE",
                "status": "RESOLVED"
            },
            {
                "id": "INC-101",
                "title": "SAP licensing",
                "rawDescription": "SAP ERP license expired code LIC-902",
                "status": "OPEN"
            }
        ],
        "threshold": 0.4
    }
    response = client.post("/ai/find-duplicates", json=payload)
    assert response.status_code == 200
    duplicates = response.json().get("duplicates", [])
    assert len(duplicates) >= 1
    assert duplicates[0]["ticketId"] == "INC-100"

def test_detect_knowledge_gaps():
    payload = {
        "noMatchTickets": [
            {"ticketId": "INC-301", "ticketText": "Kubernetes ingress controller pod crashloopbackoff"},
            {"ticketId": "INC-302", "ticketText": "Production kubernetes cluster ingress controller timeout"}
        ],
        "minClusterSize": 2
    }
    response = client.post("/ai/detect-knowledge-gaps", json=payload)
    assert response.status_code == 200
    topics = response.json().get("proposedTopics", [])
    assert len(topics) >= 1
    assert any("ingress" in t["patternKeyword"] or "kubernetes" in t["patternKeyword"] for t in topics)
