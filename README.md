# AI-Assisted Loan Eligibility Evaluation

This project implements a web-based loan evaluation system powered by a multi-agent architecture using the OpenAI API.  
We built a full-stack ML application with:
- FastAPI backend  
- HTML/CSS/JS frontend  
- AI agents (Risk, Compliance, Decision, Explanation)  
- Dynamic dashboards using Chart.js  

This project was developed for the **VT–Ecuador Group Project**.

🎥 **Demo Link:** https://youtu.be/haFGxU_iGtw

---

## 🛠️ Technologies Used

- **Frontend:** HTML, CSS, JavaScript  
- **Backend:** FastAPI (Python)  
- **AI Agents:** OpenAI API  
- **Visualization:** Chart.js  

---

## 📦 Installation

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your_username/Bank_AI.git
cd Bank_AI
```

### 2️⃣ Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3️⃣ Add Your OpenAI API Key
Inside the backend folder, create a `.env` file:

```
OPENAI_API_KEY=your_openai_key_here
```

---

## 🚀 Running the Backend
Start the FastAPI backend:

```bash
uvicorn main:app --reload
```

Backend URL:

```
http://127.0.0.1:8000
```

---

## 🌐 Running the Frontend
The frontend is located in the `frontend/` folder.

### 1️⃣ Navigate to the folder:

```bash
cd ../frontend
```

### 2️⃣ Open the frontend (choose one):

**Option A — Double-click index.html**  
Open directly in your browser.

**Option B — VS Code Live Server**  
Right-click → Open with Live Server

**Option C — Run a simple local HTTP server (recommended)**

```bash
python3 -m http.server 5500
```

Then visit:

```
http://localhost:5500
```

---

## 🔗 Connecting Frontend to Backend
The frontend sends requests to:

```
http://127.0.0.1:8000/evaluate-loan-advanced
```

If your backend runs on a different port, update this line in `frontend/script.js`:

```javascript
fetch("http://127.0.0.1:8000/evaluate-loan-advanced", {
```

---

## 🧪 Running Tests
Tests are located in the `tests/` folder.  
Run all tests with:

```bash
pytest -q
```

---

## 📁 Project Structure

```
Bank_AI/
│── backend/
│── frontend/
│── data/
│── docs/
│── report/
│── test/
│── README.md
```
5. Run the backend server
   uvicorn main:app --reload
