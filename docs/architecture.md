             ┌──────────────────────────────┐
             │            FRONTEND           │
             │  HTML / CSS / JavaScript      │
             │  - Form for user inputs       │
             │  - Dashboard visualizations    │
             └──────────────┬───────────────┘
                            │ Sends JSON (POST)
                            ▼
                ┌─────────────────────────────┐
                │           BACKEND            │
                │          FastAPI API         │
                └───────┬─────────────────────┘
                        │ /evaluate-loan-advanced
                        ▼
        ┌────────────────────────────────────────────────┐
        │                MULTI-AGENT SYSTEM               │
        │------------------------------------------------│
        │ 1. DataAgent                                   │
        │    - Processes input, computes DTI & ratios    │
        │                                                │
        │ 2. RiskAgent                                   │
        │    - Generates numeric & categorical risk      │
        │    - Adds risk reasons                         │
        │                                                │
        │ 3. ComplianceAgent                             │
        │    - Enforces minimum lending rules            │
        │                                                │
        │ 4. DecisionAgent                               │
        │    - Approve / Reject / Conditional approval   │
        │                                                │
        │ 5. ExplanationAgent                            │
        │    - Deep narrative, recommendations, interest │
        └────────────────────────────────────────────────┘
                            │
                            ▼
               ┌──────────────────────────────┐
               │         OUTPUT (JSON)         │
               │  - Final decision             │
               │  - Charts data               │
               │  - Metrics & traffic lights   │
               └──────────────┬───────────────┘
                              ▼
               ┌──────────────────────────────┐
               │        FRONTEND UI           │
               │   Renders charts & summary   │
               └──────────────────────────────┘
