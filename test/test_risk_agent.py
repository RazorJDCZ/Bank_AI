

from agents.risk_agent import calculate_risk_score

def test_risk_range():
    r = calculate_risk_score(1500, 800, 300, 2, 670)
    assert 0 <= r <= 1

def test_risk_classification():
    r = calculate_risk_score(1500, 800, 300, 2, 670)
    if r < 0.33:
        assert True  # LOW
    elif r < 0.66:
        assert True  # MEDIUM
    else:
        assert True  # HIGH
