from flask import Flask, render_template, request, redirect, send_file
import sqlite3
from reportlab.pdfgen import canvas

app = Flask(__name__)
DB = "database/expenses.db"

def init_db():
    conn = sqlite3.connect(DB)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS expenses(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item TEXT,
        amount REAL,
        category TEXT,
        co2 REAL
    )
    """)
    conn.commit()
    conn.close()

def get_tip(category):
    tips = {
        "Food": "Choose local or seasonal food.",
        "Travel": "Use bus or carpool.",
        "Shopping": "Buy only what you need.",
        "Bills": "Switch off unused appliances."
    }
    return tips.get(category, "Make eco-friendly choices!")

@app.route("/")
def home():
    init_db()

    conn = sqlite3.connect(DB)
    data = conn.execute("SELECT * FROM expenses ORDER BY id DESC").fetchall()
    total = conn.execute("SELECT IFNULL(SUM(amount),0) FROM expenses").fetchone()[0]
    carbon = conn.execute("SELECT IFNULL(SUM(co2),0) FROM expenses").fetchone()[0]
    pie = conn.execute("SELECT category,SUM(amount) FROM expenses GROUP BY category").fetchall()
    conn.close()

    labels = [e[1] for e in reversed(data)]
    co2_values = [e[4] for e in reversed(data)]
    category_labels = [p[0] for p in pie]
    category_values = [p[1] for p in pie]

    tip = "Start adding expenses."
    if data:
        tip = get_tip(data[0][3])

    return render_template(
        "index.html",
        expenses=data,
        total=total,
        carbon=carbon,
        tip=tip,
        labels=labels,
        co2_values=co2_values,
        category_labels=category_labels,
        category_values=category_values
    )

@app.route("/add", methods=["POST"])
def add():
    item = request.form["item"]
    amount = float(request.form["amount"])
    category = request.form["category"]

    factors = {"Food":0.5, "Travel":2.5, "Shopping":1.8, "Bills":0.2}
    co2 = (amount/100) * factors[category]

    conn = sqlite3.connect(DB)
    conn.execute(
        "INSERT INTO expenses(item,amount,category,co2) VALUES(?,?,?,?)",
        (item, amount, category, co2)
    )
    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/delete/<int:id>")
def delete(id):
    conn = sqlite3.connect(DB)
    conn.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/export")
def export():
    pdf = "EcoSpendAI_Report.pdf"
    c = canvas.Canvas(pdf)

    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "EcoSpendAI Report")

    conn = sqlite3.connect(DB)
    data = conn.execute(
        "SELECT item,amount,category,co2 FROM expenses"
    ).fetchall()
    conn.close()

    y = 760
    for item, amount, cat, co2 in data:
        c.drawString(
            50, y,
            f"{item} | Rs.{amount} | {cat} | CO2 {round(co2,2)} kg"
        )
        y -= 20

    c.save()
    return send_file(pdf, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)