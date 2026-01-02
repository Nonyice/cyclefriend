from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_required, current_user
import psycopg2, os
from datetime import datetime, timedelta
from auth import auth_bp
from db import get_db_connection
from utils import login_required   # if you moved it

app = Flask(__name__)
app.secret_key = "plimsoltech81"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Mypostgresdb81@localhost:5432/cycle_tracker"
)

def get_db():
    return psycopg2.connect(DATABASE_URL)

@login_manager.user_loader
def load_user(user_id):
    from auth import User
    return User.get(user_id)

app.register_blueprint(auth_bp)

@app.route("/select-mode", methods=["GET", "POST"])
@login_required
def select_mode():
    if request.method == "POST":
        mode = request.form.get("mode")

        if mode == "known":
            return redirect(url_for("known_cycle"))
        elif mode == "unknown":
            return redirect(url_for("unknown_cycle"))

    return render_template("select_mode.html")


@app.route("/dashboard", methods=["POST"])
@login_required
def dashboard():
    mode = request.form.get("mode")
    error = None
    results = None

    if mode == "known":
        last_period = datetime.strptime(
            request.form["last_period"], "%Y-%m-%d"
        ).date()
        cycle_length = int(request.form["cycle_length"])

    elif mode == "unknown":
        previous_period = datetime.strptime(
            request.form["previous_period"], "%Y-%m-%d"
        ).date()
        last_period = datetime.strptime(
            request.form["last_period"], "%Y-%m-%d"
        ).date()

        cycle_length = (last_period - previous_period).days

    # Validate cycle length
    if not (21 <= cycle_length <= 35):
        error = "Cycle length seems unusual. Please check your dates."
        return render_template("dashboard.html", error=error)

    # Calculations
    ovulation_day = last_period + timedelta(days=cycle_length - 14)
    fertile_start = ovulation_day - timedelta(days=5)
    fertile_end = ovulation_day
    next_period = last_period + timedelta(days=cycle_length)

    results = {
        "cycle_length": cycle_length,
        "ovulation_day": ovulation_day,
        "fertile_start": fertile_start,
        "fertile_end": fertile_end,
        "next_period": next_period,
    }

    return render_template("dashboard.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)
