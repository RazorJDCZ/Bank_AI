from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def sample_payload():
    return {
        "age": 30,
        "income": 5000,
        "expenses": 1500,
        "debt": 200,
        "activeLoans": 1,
        "creditScore": 680,
        "employmentType": "employee",
        "employmentYears": 3,
        "loanAmount": 10000,
        "loanTerm": 24,
        "loanPurpose": "car"
    }

def test_evaluate_endpoint_status():
    """POST should respond correctly."""
    res = client.post("/evaluate-loan-advanced", json=sample_payload())
    assert res.status_code == 200

def test_response_structure():
    """Ensure API returns all key components."""
    res = client.post("/evaluate-loan-advanced", json=sample_payload())
    data = res.json()

    for key in [
        "input_summary", "risk_analysis", "compliance_analysis",
        "final_decision", "charts", "dashboard_metrics",
        "traffic_lights", "deep_analysis", "recommendations",
        "final_conclusion", "suggested_interest_rate"
    ]:
        assert key in data

def test_risk_values_valid():
    """Check risk agent outputs the expected fields."""
    res = client.post("/evaluate-loan-advanced", json=sample_payload())
    risk = res.json()["risk_analysis"]

    assert "risk_score_numeric" in risk
    assert "risk_level" in risk
    assert "risk_percentage" in risk
    assert isinstance(risk["reasons"], list)
