from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_deploy_app_success():
    """
    Tests a successful request to the /api/deploy endpoint.
    """
    payload = {
        "email": "student@example.com",
        "secret": "my-super-secret",
        "task": "sum-of-sales-test",
        "round": 1,
        "nonce": "test-nonce",
        "brief": "A test brief.",
        "checks": [],
        "evaluation_url": "http://example.com/eval",
        "attachments": [{
            "name": "data.csv",
            "url": "data:text/csv;base64,cHJvZHVjdCxzYWxlcwpBcHBsZSwxMC41MA=="
        }]
    }
    response = client.post("/api/deploy", json=payload)

    assert response.status_code == 200
    assert "Deployment and evaluation notification successful!" in response.json()["message"]

def test_deploy_app_invalid_secret():
    """
    Tests a request with an invalid secret to the /api/deploy endpoint.
    """
    payload = {
        "email": "student@example.com",
        "secret": "wrong-secret",
        "task": "sum-of-sales-test",
        "round": 1,
        "nonce": "test-nonce",
        "brief": "A test brief.",
        "checks": [],
        "evaluation_url": "http://example.com/eval",
        "attachments": []
    }
    response = client.post("/api/deploy", json=payload)

    assert response.status_code == 403
    assert response.json()["detail"] == "Invalid secret"
