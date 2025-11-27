function goToResults() {
    // Collect data from form
    const data = {
        age: Number(document.getElementById("age").value),
        income: Number(document.getElementById("income").value),
        expenses: Number(document.getElementById("expenses").value),
        debt: Number(document.getElementById("debt").value),
        activeLoans: Number(document.getElementById("activeLoans").value),
        creditScore: Number(document.getElementById("score").value),
        employmentType: document.getElementById("employmentType").value,
        employmentYears: Number(document.getElementById("employmentYears").value),
        loanAmount: Number(document.getElementById("loanAmount").value),
        loanTerm: Number(document.getElementById("loanTerm").value),
        loanPurpose: document.getElementById("loanPurpose").value
    };

    // Save in sessionStorage to use in next page
    sessionStorage.setItem("loanFormData", JSON.stringify(data));

    // Redirect to results page
    window.location.href = "result.html";
}


// If on results page, perform evaluation
if (window.location.pathname.includes("result.html")) {
    const formData = JSON.parse(sessionStorage.getItem("loanFormData"));

    fetch("http://127.0.0.1:8000/evaluate-loan-advanced", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
    })
    .then(res => res.json())
    .then(data => {
        document.getElementById("analysis").textContent = 
            JSON.stringify(data, null, 4);
    })
    .catch(err => {
        document.getElementById("analysis").textContent = 
            "❌ Error connecting to backend: " + err;
    });
}
