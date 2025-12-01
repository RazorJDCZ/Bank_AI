# AI-Assisted Loan Eligibility Evaluation

This project implements a web-based loan evaluation system powered by a multi-agent architecture using the OpenAI API. We have made a full stack ML project with both frontend, backend and AI agentic concepts
It analyzes a user's financial profile through specialized agents (Risk, Compliance, Decision, Explanation) and generates a detailed dashboard with metrics, visualizations, summaries, recommendations, and risk-level indicators. This project is for the VT-Ecuador group project

Demo Link: https://youtu.be/haFGxU_iGtw 
---

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** FastAPI (Python)  
- **AI Agents:** OpenAI API  
- **Visualization:** Chart.js  

---

## 📦 Installation

```bash
1. Clone the repository
   git clone https://github.com/your_username/Bank_AI.git
   cd Bank_AI

2. Navigate to the backend folder
   cd backend

3. Install all Python dependencies
   pip install -r requirements.txt

4. Create the .env file with your OpenAI API key
   (inside the backend folder)

   Add inside the file:
   OPENAI_API_KEY=your_openai_key_here

5. Run the backend server
   uvicorn main:app --reload
