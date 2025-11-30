
// FORM → RESULTS REDIRECT

function goToResults() {
    const required = [
        "age", "income", "expenses", "debt",
        "activeLoans", "score", "employmentYears",
        "loanAmount", "loanTerm"
    ];

    for (const id of required) {
        const val = document.getElementById(id).value;
        if (!val || isNaN(Number(val))) {
            alert(`Missing or invalid field: ${id}`);
            return;
        }
    }

    const data = {
        age: Number(age.value),
        income: Number(income.value),
        expenses: Number(expenses.value),
        debt: Number(debt.value),
        activeLoans: Number(activeLoans.value),
        creditScore: Number(score.value),
        employmentType: employmentType.value,
        employmentYears: Number(employmentYears.value),
        loanAmount: Number(loanAmount.value),
        loanTerm: Number(loanTerm.value),
        loanPurpose: loanPurpose.value
    };

    sessionStorage.setItem("loanFormData", JSON.stringify(data));
    window.location.href = "result.html";
}



// RESULTS PAGE LOGIC

if (window.location.pathname.includes("result.html")) {
    const formData = JSON.parse(sessionStorage.getItem("loanFormData") || "{}");

    fetch("http://127.0.0.1:8000/evaluate-loan-advanced", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    })
        .then(res => res.json())
        .then(data => {
            renderDecision(data);
            renderExecutiveSummary(data);
            renderRiskGauge(data);
            renderMetricsChart(data);
            renderDTIChart(data);
            renderAffordChart(data);
            renderScoreChart(data);
            renderLTIChart(data);
            renderAgentAnalysis(data);
            renderTextAnalysis(data);
        })
        .catch(err => {
            document.getElementById("decisionText").textContent =
                "Error connecting to backend: " + err;
        });
}



// DECISION + BADGE

function renderDecision(api) {
    const d = api.final_decision;
    decisionText.textContent = d.decision;
    decisionReason.textContent = d.short_reason;

    if (d.decision === "APPROVED")
        decisionBadge.className = "badge badge-approve";
    else if (d.decision === "CONDITIONAL APPROVAL")
        decisionBadge.className = "badge badge-conditional";
    else
        decisionBadge.className = "badge badge-reject";
}



// EXECUTIVE SUMMARY + TRAFFIC LIGHTS

function renderExecutiveSummary(api) {
    const metrics = api.dashboard_metrics;
    const risk = api.risk_analysis;
    const lights = api.traffic_lights;

    // Semáforos
    const container = document.getElementById("trafficIndicators");
    container.innerHTML = "";

    const items = [
        { label: `Risk level: ${risk.risk_level.toUpperCase()}`, color: lights.risk },
        {
            label: `Affordability: installment uses ${(metrics.installment_to_free_income * 100).toFixed(1)}% of free income`,
            color: lights.affordability
        },
        {
            label: `Compliance: ${api.compliance_analysis.status === "pass" ? "requirements met" : "requirements not met"}`,
            color: lights.compliance
        }
    ];

    items.forEach(it => {
        const div = document.createElement("div");
        div.className = "traffic-item";
        div.innerHTML = `<span class="status-dot ${it.color}"></span><span>${it.label}</span>`;
        container.appendChild(div);
    });

    // Bullets resumen ejecutivo
    const ul = document.getElementById("execSummaryList");
    ul.innerHTML = "";
    const bullets = [
        `DTI: ${metrics.dti.toFixed(2)} (ratio of total debt + expenses to income).`,
        `Estimated installment: ${metrics.estimated_installment.toFixed(2)} vs free income of ${metrics.monthly_free.toFixed(2)}.`,
        `Loan-to-income ratio (annual): ${(metrics.loan_to_income_ratio * 100).toFixed(1)}%.`,
        `Overall risk assessment: ${risk.risk_level.toUpperCase()} with ${risk.risk_percentage.toFixed(1)}% estimated risk.`,
    ];
    bullets.forEach(b => {
        const li = document.createElement("li");
        li.textContent = b;
        ul.appendChild(li);
    });
}



// RISK GAUGE

let gaugeChart;
function renderRiskGauge(api) {
    const risk = api.risk_analysis;
    const value = risk.risk_percentage;
    const ctx = document.getElementById("riskGauge").getContext("2d");
    if (gaugeChart) gaugeChart.destroy();

    gaugeChart = new Chart(ctx, {
        type: "doughnut",
        data: {
            labels: ["Risk", "Safe"],
            datasets: [{
                data: [value, 100 - value],
                backgroundColor: [
                    value < 40 ? "#4caf50" : value < 70 ? "#ff9800" : "#f44336",
                    "rgba(255,255,255,0.06)"
                ],
                borderWidth: 0
            }]
        },
        options: {
            circumference: 180,
            rotation: -90,
            cutout: "70%",
            plugins: { legend: { display: false }, tooltip: { enabled: false } }
        }
    });

    gaugeLabel.textContent = value.toFixed(1) + "%";
    riskLabel.textContent = `Risk level: ${risk.risk_level.toUpperCase()}`;
}



// KEY FINANCIAL METRICS (Income / Expenses / Debt)

let incomeChart;
function renderMetricsChart(api) {
    const ch = api.charts.income_vs_expenses;
    const ctx = document.getElementById("incomeChart").getContext("2d");
    if (incomeChart) incomeChart.destroy();

    metricsText.textContent =
        `Monthly income: ${ch.income.toFixed(2)} | Expenses: ${ch.expenses.toFixed(2)} | Debt: ${ch.debt.toFixed(2)}`;

    incomeChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Income", "Expenses", "Debt"],
            datasets: [{
                data: [ch.income, ch.expenses, ch.debt],
                backgroundColor: ["#d4af37", "#b8860b", "#8b5a00"],
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                x: { grid: { display: false } },
                y: { grid: { color: "rgba(255,255,255,0.08)" } }
            }
        }
    });
}



// DTI SCENARIOS CHART

let dtiChart;
function renderDTIChart(api) {
    const d = api.charts.dti_simulation;
    const ctx = document.getElementById("dtiChart").getContext("2d");
    if (dtiChart) dtiChart.destroy();

    dtiChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Current", "-10% debt", "-20% debt", "-30% debt"],
            datasets: [{
                data: [d.current, d.minus10, d.minus20, d.minus30],
                backgroundColor: ["#f44336", "#ff9800", "#ffca28", "#4caf50"]
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                y: { grid: { color: "rgba(255,255,255,0.08)" } }
            }
        }
    });
}



// AFFORDABILITY CHART

let affordChart;
function renderAffordChart(api) {
    const a = api.charts.affordability;
    const ctx = document.getElementById("affordChart").getContext("2d");
    if (affordChart) affordChart.destroy();

    affordChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Installment", "Free income"],
            datasets: [{
                data: [a.installment, a.free_income],
                backgroundColor: ["#f44336", "#4caf50"]
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { grid: { color: "rgba(255,255,255,0.08)" } } }
        }
    });
}



// CREDIT SCORE CHART

let scoreChart;
function renderScoreChart(api) {
    const s = api.charts.credit_score.score;
    const ctx = document.getElementById("scoreChart").getContext("2d");
    if (scoreChart) scoreChart.destroy();

    scoreChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Applicant score"],
            datasets: [{
                data: [s],
                backgroundColor: s >= 700 ? "#4caf50" : s >= 650 ? "#ffca28" : "#f44336"
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: {
                y: {
                    min: 300,
                    max: 900,
                    grid: { color: "rgba(255,255,255,0.08)" }
                }
            }
        }
    });
}



// LOAN TO INCOME CHART

let ltiChart;
function renderLTIChart(api) {
    const r = api.charts.loan_to_income.ratio * 100;
    const ctx = document.getElementById("ltiChart").getContext("2d");
    if (ltiChart) ltiChart.destroy();

    ltiChart = new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Loan / Annual Income"],
            datasets: [{
                data: [r],
                backgroundColor: r < 30 ? "#4caf50" : r < 60 ? "#ff9800" : "#f44336"
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            scales: { y: { grid: { color: "rgba(255,255,255,0.08)" } } }
        }
    });
}



// AGENT ANALYSIS (Risk + Compliance)

function renderAgentAnalysis(api) {
    const risk = api.risk_analysis;
    const comp = api.compliance_analysis;
    let html = "";

    html += "<strong>Risk Agent:</strong><ul>";
    if (risk.reasons.length === 0) {
        html += "<li>No major risk factors detected.</li>";
    } else {
        risk.reasons.forEach(r => html += `<li>${r}</li>`);
    }
    html += "</ul><br>";

    html += "<strong>Compliance Agent:</strong><br>";
    if (comp.status === "pass") {
        html += "<span class='muted'>All minimum requirements were met.</span>";
    } else {
        html += "<ul>";
        comp.reasons.forEach(r => html += `<li>${r}</li>`);
        html += "</ul>";
    }

    agentAnalysis.innerHTML = html;
}


// TEXT ANALYSIS (DEEP, RECOMMENDATIONS, CONCLUSION, INTEREST)

function renderTextAnalysis(api) {
    deepAnalysis.textContent = api.deep_analysis;
    recommendations.textContent = api.recommendations;
    finalConclusion.textContent = api.final_conclusion;
    interestRate.textContent = api.suggested_interest_rate;
}



// COLLAPSIBLE CARDS

function toggleCollapse(bodyId) {
    const body = document.getElementById(bodyId);
    const icon = document.getElementById("icon-" + bodyId);
    const isCollapsed = body.classList.toggle("collapsed");
    if (icon) {
        icon.textContent = isCollapsed ? "▲" : "▼";
    }
}
