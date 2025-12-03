
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_negative_values():
    response = client.post("/evaluate-loan-advanced", json={
        "age": -1,
        "income": -500,
        "expenses": 0,
        "debt": 0,
        "active_loans": 0,
        "credit_score": 0,
        "employment_type": "employee",
        "employment_years": 0,
        "loan_amount": 0,
        "loan_term": 0,
        "loan_purpose": "consumption"
    })

    assert response.status_code == 422
