from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS habits
                 (id INTEGER PRIMARY KEY,
                  name TEXT NOT NULL,
                  date TEXT NOT NULL,
                  completed INTEGER DEFAULT 0)''')
    conn.commit()
    conn.close()

def get_streak(habit_name):
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("""
        SELECT date, completed FROM habits 
        WHERE name=? 
        ORDER BY date DESC
    """, (habit_name,))
    rows = c.fetchall()
    conn.close()
    streak = 0
    for row in rows:
        if row[1] == 1:
            streak += 1
        else:
            break
    return streak

init_db()

@app.route("/")
def home():
    today = str(date.today())
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT * FROM habits WHERE date=?", (today,))
    habits = c.fetchall()
    conn.close()

    habits_with_streak = []
    for habit in habits:
        streak = get_streak(habit[1])
        habits_with_streak.append(habit + (streak,))
    habits = habits_with_streak

    total = len(habits)
    completed = sum(1 for h in habits if h[3] == 1)
    percent = round((completed/total)*100) if total > 0 else 0

    return render_template("index.html",
                         habits=habits,
                         today=today,
                         percent=percent,
                         completed=completed,
                         total=total)

@app.route("/add", methods=["POST"])
def add():
    habit = request.form.get("habit")
    today = str(date.today())
    if habit:
        conn = sqlite3.connect('habits.db')
        c = conn.cursor()
        c.execute("INSERT INTO habits (name, date, completed) VALUES (?,?,0)",
                 (habit, today))
        conn.commit()
        conn.close()
    return redirect("/")

@app.route("/toggle/<int:id>", methods=["POST"])
def toggle(id):
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT completed FROM habits WHERE id=?", (id,))
    habit = c.fetchone()
    if habit:
        new_status = 0 if habit[0] == 1 else 1
        c.execute("UPDATE habits SET completed=? WHERE id=?",
                 (new_status, id))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("DELETE FROM habits WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")

@app.route("/history")
def history():
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()
    c.execute("SELECT date, COUNT(*), SUM(completed) FROM habits GROUP BY date ORDER BY date DESC")
    history = c.fetchall()
    conn.close()
    return render_template("history.html", history=history)

if __name__ == "__main__":
    app.run(debug=True)