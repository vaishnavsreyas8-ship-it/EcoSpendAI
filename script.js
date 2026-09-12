const form = document.getElementById("expenseForm");

form.addEventListener("submit", function(e){
    e.preventDefault();

    const item = document.getElementById("item").value;
    const amount = parseFloat(document.getElementById("amount").value);
    const category = document.getElementById("category").value;

    let score = 100;

    if(category === "Transport") score -= 20;
    if(category === "Shopping") score -= 15;
    if(category === "Food") score -= 8;

    if(amount > 500) score -= 10;
    if(amount > 1000) score -= 10;

    let tip = "🌱 Great eco-friendly spending!";

    if(score < 80)
        tip = "🚲 Try walking or public transport to reduce emissions.";
    if(score < 60)
        tip = "♻️ Consider sustainable alternatives before buying.";

    document.getElementById("result").innerHTML =
    `<h3>${item}</h3>
     <p>Amount: ₹${amount}</p>
     <p>Eco Score: <b>${score}/100</b></p>
     <p>${tip}</p>`;

    form.reset();
});