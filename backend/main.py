from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Dict, Any

app = FastAPI(
    title="AI-Assisted Loan Eligibility Evaluation API",
    description="Multi-agent pipeline for loan evaluation with full dashboard.",
    version="3.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
#  INPUT MODEL
# -----------------------------
class LoanApplication(BaseModel):
    age: int = Field(..., ge=18)
    income: float = Field(..., ge=0)
    expenses: float = Field(..., ge=0)
    debt: float = Field(..., ge=0)
    activeLoans: int = Field(..., ge=0)
    creditScore: int = Field(..., ge=0, le=900)
    employmentType: Literal["employee", "independent", "contract", "unemployed"]
    employmentYears: float = Field(..., ge=0)
    loanAmount: float = Field(..., ge=0)
    loanTerm: int = Field(..., ge=1)
    loanPurpose: Literal["consumption", "car", "education", "business", "house", "other"]


# -----------------------------
#  AGENT 1 – DATA AGENT
# -----------------------------
class DataAgent:
    def process(self, d: LoanApplication) -> Dict[str, Any]:
        dti = (d.debt + d.expenses) / d.income if d.income > 0 else 1e9
        surplus = d.income - d.expenses
        return {
            "age": d.age,
            "income": d.income,
            "expenses": d.expenses,
            "debt": d.debt,
            "active_loans": d.activeLoans,
            "credit_score": d.creditScore,
            "employment_type": d.employmentType,
            "employment_years": d.employmentYears,
            "loan_amount": d.loanAmount,
            "loan_term": d.loanTerm,
            "loan_purpose": d.loanPurpose,
            "dti": dti,
            "income_after_expenses": surplus
        }


# -----------------------------
#  AGENT 2 – RISK AGENT
# -----------------------------
class RiskAgent:
    def evaluate(self, p: Dict[str, Any]) -> Dict[str, Any]:
        risk_score = 0
        reasons = []

        dti = p["dti"]
        if dti > 0.6:
            risk_score += 3
            reasons.append("Debt-to-income ratio is very high.")
        elif dti > 0.45:
            risk_score += 2
            reasons.append("Debt-to-income ratio is moderately high.")
        elif dti > 0.30:
            risk_score += 1
            reasons.append("Debt-to-income ratio is slightly elevated.")

        cs = p["credit_score"]
        if cs < 550:
            risk_score += 3
            reasons.append("Very low credit score.")
        elif cs < 650:
            risk_score += 2
            reasons.append("Low credit score.")
        elif cs < 700:
            risk_score += 1
            reasons.append("Moderate credit score.")

        if p["employment_years"] < 1 and p["employment_type"] != "independent":
            risk_score += 1
            reasons.append("Short employment history in current job.")

        if p["active_loans"] >= 4:
            risk_score += 2
            reasons.append("There are several active loans.")

        if p["loan_amount"] > p["income"] * 15:
            risk_score += 2
            reasons.append("Requested amount is very high relative to income.")
        elif p["loan_amount"] > p["income"] * 10:
            risk_score += 1
            reasons.append("Requested amount is high relative to income.")

        if risk_score >= 6:
            level = "high"
        elif risk_score >= 3:
            level = "medium"
        else:
            level = "low"

        if level == "low":
            risk_percent = 20 + risk_score * 4
        elif level == "medium":
            risk_percent = 40 + risk_score * 7
        else:
            risk_percent = 70 + risk_score * 5

        return {
            "risk_score_numeric": risk_score,
            "risk_level": level,
            "risk_percentage": min(100, risk_percent),
            "reasons": reasons
        }


# -----------------------------
#  AGENT 3 – COMPLIANCE AGENT
# -----------------------------
class ComplianceAgent:
    def check(self, p: Dict[str, Any]) -> Dict[str, Any]:
        reasons = []
        if p["income"] < 400:
            reasons.append("Income is below the minimum threshold.")
        if p["employment_type"] == "unemployed":
            reasons.append("Applicant is unemployed.")
        if p["employment_years"] < 0.5 and p["employment_type"] != "independent":
            reasons.append("Employment stability is very low.")
        if p["credit_score"] < 500:
            reasons.append("Credit score is below the minimum allowed.")
        status = "pass" if not reasons else "fail"
        return {"status": status, "reasons": reasons}


# -----------------------------
#  AGENT 4 – DECISION AGENT
# -----------------------------
class DecisionAgent:
    def decide(self, p, risk, compliance):
        if compliance["status"] == "fail":
            return {
                "decision": "REJECTED",
                "short_reason": "Minimum bank requirements were not met.",
                "category": "compliance_fail"
            }
        if risk["risk_level"] == "high":
            return {
                "decision": "REJECTED",
                "short_reason": "Overall risk is too high to approve safely.",
                "category": "high_risk"
            }
        if risk["risk_level"] == "medium":
            return {
                "decision": "CONDITIONAL APPROVAL",
                "short_reason": "Medium risk. Loan should be approved with conditions.",
                "category": "medium_risk"
            }
        return {
            "decision": "APPROVED",
            "short_reason": "Risk profile is acceptable for approval.",
            "category": "low_risk"
        }


# -----------------------------
#  AGENT 5 – EXPLANATION AGENT
# -----------------------------
class ExplanationAgent:
    """
    Generates deep financial analysis, extended recommendations,
    and a full professional narrative of the decision.
    """

    def explain(self, p, risk, compliance, decision):

        dti = p["dti"]
        monthly_free = p["income_after_expenses"]
        income = p["income"]
        expenses = p["expenses"]
        debt = p["debt"]
        score = p["credit_score"]
        loans = p["active_loans"]
        loan_amount = p["loan_amount"]
        term = p["loan_term"]

        # Suggested interest rate band based on risk %
        r = risk["risk_percentage"]
        if r < 35:
            interest = "8% – 11%"
        elif r < 60:
            interest = "12% – 16%"
        elif r < 80:
            interest = "17% – 22%"
        else:
            interest = "23% – 32% (very high risk segment)"

        deep = f"""
The applicant's financial profile shows a combination of strengths and structural vulnerabilities that must be 
carefully balanced. The current debt-to-income (DTI) ratio is {dti:.2f}, which places the case in the 
{risk['risk_level'].upper()} risk band. Ratios above 0.50 are usually associated with limited flexibility to absorb 
unexpected expenses or income drops, so this indicator is a central driver of the overall risk classification.

Monthly residual income after covering reported expenses is {monthly_free:.2f}. This value represents the 
actual liquidity available to service new debt and is more relevant than the gross income figure of {income:.2f}. 
When combining expenses and existing debt obligations, they absorb approximately {((expenses + debt) / income) * 100:.1f}% 
of the monthly income, which indicates a moderately stressed budget.

The credit score of {score} suggests a history with some delays, limited credit depth, or a mix of credit products 
that has not always been optimally managed. The presence of {loans} active loans amplifies this risk, since households 
with multiple ongoing obligations are more exposed to interest accumulation and administrative complexity.

Employment stability of {p['employment_years']:.1f} years provides a partial anchor to the analysis. While this is not 
a weak point, a longer and more consistent work history would further reduce risk. The requested amount of {loan_amount:.2f} 
over {term} months may be affordable under current conditions, but it leaves limited buffer if interest rates increase or 
if personal income is temporarily reduced.
"""

        rec = """
Based on the current indicators, the following actions are recommended to improve the applicant’s risk profile:

• Reduce outstanding debt, prioritizing products with the highest interest rates, to bring the DTI closer to the 0.30–0.35 range.  
• Avoid opening new credit lines or increasing credit card limits during the next 6–12 months.  
• Improve credit score by paying installments before the due date and avoiding missed payments.  
• Build a small emergency fund so that unexpected events do not directly affect repayment capacity.  
• Renegotiate or consolidate some existing debts if there are multiple small obligations with high rates.  
• Consider requesting a slightly lower loan amount or a longer term to reduce monthly payment pressure.  
• Maintain employment stability and, when possible, document income growth or promotion perspectives.  
"""

        conclusion = f"""
Final decision: {decision['decision']}.
{decision['short_reason']}

From a prudential perspective, the applicant does not present an extreme risk profile, but the combination of 
DTI, credit score and multi-loan exposure requires conservative conditions. Under the current situation, 
the loan is better positioned as a conditional or tightly monitored approval rather than a standard product.

If the recommended measures are implemented — particularly debt reduction and credit score improvement — 
the applicant could migrate to a significantly stronger risk category within 4–8 months. At that point, 
renegotiation of conditions or access to more favorable rates would be technically justified.
"""

        return {
            "deep_analysis": deep.strip(),
            "recommendations": rec.strip(),
            "final_conclusion": conclusion.strip(),
            "suggested_interest_rate": interest.strip()
        }


# -----------------------------
#  DASHBOARD METRICS + CHART DATA
# -----------------------------
def build_dashboard(p: Dict[str, Any], risk: Dict[str, Any], compliance: Dict[str, Any]):
    income = p["income"]
    expenses = p["expenses"]
    debt = p["debt"]
    monthly_free = p["income_after_expenses"]
    loan_amount = p["loan_amount"]
    term = p["loan_term"]
    dti = p["dti"]
    score = p["credit_score"]

    # Loan installment estimation (simple amortization with risk-based rate)
    if risk["risk_level"] == "low":
        annual_rate = 0.14
    elif risk["risk_level"] == "medium":
        annual_rate = 0.18
    else:
        annual_rate = 0.24

    monthly_rate = annual_rate / 12 if term > 0 else 0
    if monthly_rate > 0 and term > 0:
        factor = (monthly_rate * (1 + monthly_rate) ** term) / ((1 + monthly_rate) ** term - 1)
        installment = loan_amount * factor
    else:
        installment = loan_amount / term if term > 0 else 0

    inst_to_free = installment / monthly_free if monthly_free > 0 else 10.0
    loan_to_income = loan_amount / (income * 12) if income > 0 else 0
    expense_ratio = (expenses + debt) / income if income > 0 else 1

    # DTI simulation with debt reduction
    def dti_with_factor(f):
        if income <= 0:
            return dti
        return ((debt * f) + expenses) / income

    dti10 = dti_with_factor(0.9)
    dti20 = dti_with_factor(0.8)
    dti30 = dti_with_factor(0.7)

    # Traffic light logic
    if risk["risk_level"] == "low":
        risk_light = "green"
    elif risk["risk_level"] == "medium":
        risk_light = "yellow"
    else:
        risk_light = "red"

    if inst_to_free < 0.30:
        afford_light = "green"
    elif inst_to_free < 0.50:
        afford_light = "yellow"
    else:
        afford_light = "red"

    compliance_light = "green" if compliance["status"] == "pass" else "red"

    charts = {
        "risk_gauge": {"value": risk["risk_percentage"]},
        "income_vs_expenses": {
            "income": income,
            "expenses": expenses,
            "debt": debt
        },
        "dti_simulation": {
            "current": dti,
            "minus10": dti10,
            "minus20": dti20,
            "minus30": dti30
        },
        "affordability": {
            "installment": installment,
            "free_income": monthly_free
        },
        "credit_score": {
            "score": score
        },
        "loan_to_income": {
            "ratio": loan_to_income
        }
    }

    metrics = {
        "dti": dti,
        "monthly_free": monthly_free,
        "expense_ratio": expense_ratio,
        "estimated_installment": installment,
        "installment_to_free_income": inst_to_free,
        "loan_to_income_ratio": loan_to_income
    }

    traffic_lights = {
        "risk": risk_light,
        "affordability": afford_light,
        "compliance": compliance_light
    }

    return charts, metrics, traffic_lights


# -----------------------------
#  ENDPOINT
# -----------------------------
@app.post("/evaluate-loan-advanced")
def evaluate(application: LoanApplication):
    data = DataAgent().process(application)
    risk = RiskAgent().evaluate(data)
    compliance = ComplianceAgent().check(data)
    decision = DecisionAgent().decide(data, risk, compliance)
    explanation = ExplanationAgent().explain(data, risk, compliance, decision)
    charts, metrics, lights = build_dashboard(data, risk, compliance)

    return {
        "input_summary": data,
        "risk_analysis": risk,
        "compliance_analysis": compliance,
        "final_decision": decision,
        "charts": charts,
        "dashboard_metrics": metrics,
        "traffic_lights": lights,
        "deep_analysis": explanation["deep_analysis"],
        "recommendations": explanation["recommendations"],
        "final_conclusion": explanation["final_conclusion"],
        "suggested_interest_rate": explanation["suggested_interest_rate"]
    }


@app.get("/")
def root():
    return {"message": "AI Loan Evaluation backend running"}
