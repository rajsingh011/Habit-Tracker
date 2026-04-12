from flask import Flask, render_template, request, redirect

app = Flask(__name__)

habits = []

@app.route("/")
def home():
    return render_template("index.html", habits=habits)

@app.route("/add", methods=["POST"])
def add():
    habit = request.form.get("habit")
    if habit:
        habits.append(habit)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)