from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any
import os

# Si luego quieres usar OpenAI de verdad:
try:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
except Exception:
    client = None  # No rompe si no está configurado aún

# -------------------------
#   FASTAPI APP
# -------------------------

app = FastAPI(
    title="AI-Assisted Loan Eligibility Evaluation API",
    description="Backend with agent-based evaluation for loan eligibility.",
    version="1.0.0"
)

# Permitir llamadas desde tu HTML (misma máquina)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # si quieres, luego restringes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
#   DATA MODEL
# -------------------------

class LoanApplication(BaseModel):
    age: int = Field(..., ge=18, description="Applicant age")
    income: float = Field(..., ge=0, description="Monthly income")
    expenses: float = Field(..., ge=0, description="Monthly expenses")
    debt: float = Field(..., ge=0, description="Total current debt")
    activeLoans: int = Field(..., ge=0, description="Number of active loans")
    creditScore: int = Field(..., ge=0, le=900, description="Credit score")
    employmentType: Literal["employee", "independent", "contract", "unemployed"]
    employmentYears: float = Field(..., ge=0, description="Years in current job")
    loanAmount: float = Field(..., ge=0, description="Requested loan amount")
    loanTerm: int = Field(..., ge=1, description="Loan term in months")
    loanPurpose: Literal["consumption", "car", "education", "business", "house", "other"]


# -------------------------
#   AGENTES
# -------------------------

class DataAgent:
    """Valida y prepara los datos básicos del solicitante."""
    def process(self, app_data: LoanApplication) -> Dict[str, Any]:
        dti = (app_data.debt + app_data.expenses) / app_data.income if app_data.income > 0 else 1e9
        income_after_expenses = app_data.income - app_data.expenses

        return {
            "age": app_data.age,
            "income": app_data.income,
            "expenses": app_data.expenses,
            "debt": app_data.debt,
            "active_loans": app_data.activeLoans,
            "credit_score": app_data.creditScore,
            "employment_type": app_data.employmentType,
            "employment_years": app_data.employmentYears,
            "loan_amount": app_data.loanAmount,
            "loan_term": app_data.loanTerm,
            "loan_purpose": app_data.loanPurpose,
            "dti": dti,
            "income_after_expenses": income_after_expenses
        }


class RiskAgent:
    """Evalúa el riesgo financiero basado en DTI, score, estabilidad y monto."""
    def evaluate(self, processed: Dict[str, Any]) -> Dict[str, Any]:
        risk_score = 0
        reasons = []

        dti = processed["dti"]
        if dti > 0.6:
            risk_score += 3
            reasons.append("Debt-to-income ratio is very high.")
        elif dti > 0.45:
            risk_score += 2
            reasons.append("Debt-to-income ratio is moderately high.")
        elif dti > 0.30:
            risk_score += 1
            reasons.append("Debt-to-income ratio is slightly elevated.")

        cs = processed["credit_score"]
        if cs < 550:
            risk_score += 3
            reasons.append("Very low credit score.")
        elif cs < 650:
            risk_score += 2
            reasons.append("Low credit score.")
        elif cs < 700:
            risk_score += 1
            reasons.append("Moderate credit score.")

        if processed["employment_years"] < 1 and processed["employment_type"] in ["employee", "contract"]:
            risk_score += 1
            reasons.append("Short employment history in current job.")

        if processed["active_loans"] >= 4:
            risk_score += 2
            reasons.append("There are several active loans.")

        if processed["loan_amount"] > processed["income"] * 15:
            risk_score += 2
            reasons.append("Requested amount is very high relative to income.")
        elif processed["loan_amount"] > processed["income"] * 10:
            risk_score += 1
            reasons.append("Requested amount is high relative to income.")

        risk_level = "low"
        if risk_score >= 6:
            risk_level = "high"
        elif risk_score >= 3:
            risk_level = "medium"

        return {
            "risk_score_numeric": risk_score,
            "risk_level": risk_level,
            "reasons": reasons
        }


class ComplianceAgent:
    """Verifica requisitos mínimos del banco (edad, ingresos, empleo, score mínimo)."""
    def check(self, processed: Dict[str, Any]) -> Dict[str, Any]:
        reasons = []

        if processed["age"] < 18:
            reasons.append("Applicant is under the minimum age requirement.")

        if processed["income"] < 400:
            reasons.append("Monthly income is below the minimum threshold.")

        if processed["employment_type"] == "unemployed":
            reasons.append("Applicant is currently unemployed.")

        if processed["employment_years"] < 0.5 and processed["employment_type"] != "independent":
            reasons.append("Applicant has very low stability in current job.")

        if processed["credit_score"] < 500:
            reasons.append("Credit score is below the minimum required.")

        status = "pass" if len(reasons) == 0 else "fail"

        return {
            "status": status,
            "reasons": reasons
        }


class DecisionAgent:
    """Combina compliance + riesgo y decide: APPROVED / REJECTED / CONDITIONAL."""
    def decide(
        self,
        processed: Dict[str, Any],
        risk: Dict[str, Any],
        compliance: Dict[str, Any]
    ) -> Dict[str, Any]:

        if compliance["status"] == "fail":
            return {
                "decision": "REJECTED",
                "reason": "Did not meet minimum bank requirements.",
                "details": {
                    "compliance_issues": compliance["reasons"],
                    "risk_level": risk["risk_level"],
                    "risk_reasons": risk["reasons"]
                }
            }

        # Si pasa compliance, revisamos riesgo
        if risk["risk_level"] == "high":
            return {
                "decision": "REJECTED",
                "reason": "Financial risk is too high.",
                "details": {
                    "compliance_issues": [],
                    "risk_level": risk["risk_level"],
                    "risk_reasons": risk["reasons"]
                }
            }

        if risk["risk_level"] == "medium":
            # Aprobación condicional
            return {
                "decision": "CONDITIONAL APPROVAL",
                "reason": "Medium risk. Suggested to lower loan amount or adjust terms.",
                "details": {
                    "suggested_max_amount": round(processed["income"] * 8, 2),
                    "risk_level": risk["risk_level"],
                    "risk_reasons": risk["reasons"]
                }
            }

        # Riesgo bajo + compliance ok
        return {
            "decision": "APPROVED",
            "reason": "Applicant meets minimum requirements with acceptable risk.",
            "details": {
                "risk_level": risk["risk_level"],
                "risk_reasons": risk["reasons"]
            }
        }


class ExplanationAgent:
    """
    Opcional: usa OpenAI para generar un análisis en lenguaje natural
    basado en los resultados de los agentes anteriores.
    """
    def explain(
        self,
        processed: Dict[str, Any],
        risk: Dict[str, Any],
        compliance: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> str:

        # Si no hay cliente OpenAI configurado, devolvemos una explicación manual simple
        if client is None:
            return (
                f"Decision: {decision['decision']}. "
                f"Reason: {decision['reason']}. "
                f"Key factors considered: debt-to-income ratio, credit score, "
                f"employment stability, and basic bank eligibility rules."
            )

        # Si quieres usar OpenAI de verdad:
        prompt = f"""
You are a loan officer. Based on the following data, write a clear, concise explanation
(around 150-200 words) of why the applicant was APPROVED, REJECTED, or CONDITIONALLY APPROVED.

Processed data: {processed}
Risk evaluation: {risk}
Compliance check: {compliance}
Final decision: {decision}

Explain in neutral, professional English. Mention main strengths and weaknesses.
"""

        try:
            # Ejemplo con Responses API moderna:
            response = client.responses.create(
                model="gpt-4.1-mini",
                input=prompt,
            )
            text = response.output[0].content[0].text
            return text
        except Exception as e:
            return (
                f"Decision: {decision['decision']}. "
                f"Reason: {decision['reason']}. "
                f"(Explanation agent failed: {e})"
            )


# -------------------------
#   ENDPOINT PRINCIPAL
# -------------------------

@app.post("/evaluate-loan-advanced")
def evaluate_loan_advanced(application: LoanApplication):
    data_agent = DataAgent()
    risk_agent = RiskAgent()
    compliance_agent = ComplianceAgent()
    decision_agent = DecisionAgent()
    explanation_agent = ExplanationAgent()

    processed = data_agent.process(application)
    risk_result = risk_agent.evaluate(processed)
    compliance_result = compliance_agent.check(processed)
    decision_result = decision_agent.decide(processed, risk_result, compliance_result)
    explanation_text = explanation_agent.explain(
        processed, risk_result, compliance_result, decision_result
    )

    return {
        "input_summary": processed,
        "risk_analysis": risk_result,
        "compliance_analysis": compliance_result,
        "final_decision": decision_result,
        "natural_language_explanation": explanation_text
    }


@app.get("/")
def root():
    return {"message": "Loan Evaluation API is running."}
