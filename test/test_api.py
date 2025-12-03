

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api_health():
    response = client.post("/evaluate-loan-advanced", json={
        "age": 30,
        "income": 1500,
        "expenses": 800,
        "debt": 300,
        "active_loans": 2,
        "credit_score": 670,
        "employment_type": "employee",
        "employment_years": 2,
        "loan_amount": 1000,
        "loan_term": 36,
        "loan_purpose": "consumption"
    })

    assert response.status_code == 200
    data = response.json()
    
    assert "decision" in data
    assert "risk_score" in data
    assert "recommendations" in data
