from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, login_required, current_user
import psycopg2, os
from datetime import datetime, timedelta
from auth import auth_bp
from db import get_db_connection
from utils import login_required   # if you moved it
from flask_login import UserMixin

from datetime import datetime

@app.context_processor
def inject_datetime():
    return {"datetime": datetime}


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username



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

@app.route("/")
def home():
    return redirect(url_for("auth.login"))


@app.route("/select-mode", methods=["GET", "POST"])
@login_required
def select_mode():
    if request.method == "POST":
        mode = request.form.get("mode")

        if mode == "known":
            return redirect(url_for("known_cycle"))
        elif mode == "unknown":
            return redirect(url_for("unknown_cycle"))

    return render_template("mode.html")

@app.route("/known-cycle", methods=["GET", "POST"])
@login_required
def known_cycle():
    if request.method == "POST":
        last_period = request.form.get("last_period")
        cycle_length = int(request.form.get("cycle_length"))

        # ---- computation logic ----
        # next_period = last_period + cycle_length
        # fertile_window, ovulation, etc.

        return redirect(url_for("dashboard"))

    return render_template("known_cycle.html")

@app.route("/unknown-cycle", methods=["GET", "POST"])
@login_required
def unknown_cycle():
    if request.method == "POST":
        previous_period = request.form.get("previous_period")
        last_period = request.form.get("last_period")

        # ---- computation logic ----
        # cycle_length = difference between the two dates
        # then compute predictions

        return redirect(url_for("dashboard"))

    return render_template("unknown_cycle.html")



@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    results = None
    error = None

    if request.method == "POST":
        mode = request.form.get("mode")
        cycle_length = None  # 🔑 always initialize

        try:
            # =============================
            # MODE 1: USER KNOWS CYCLE
            # =============================
            if mode == "known":
                last_period_str = request.form.get("last_period")
                cycle_length_str = request.form.get("cycle_length")

                if not last_period_str or not cycle_length_str:
                    error = "Please provide both last period date and cycle length."
                else:
                    last_period = datetime.strptime(last_period_str, "%Y-%m-%d").date()
                    cycle_length = int(cycle_length_str)

            # =============================
            # MODE 2: USER DOES NOT KNOW CYCLE
            # =============================
            elif mode == "unknown":
                previous_period_str = request.form.get("previous_period")
                last_period_str = request.form.get("last_period")

                if not previous_period_str or not last_period_str:
                    error = "Please provide both menstrual dates."
                else:
                    previous_period = datetime.strptime(previous_period_str, "%Y-%m-%d").date()
                    last_period = datetime.strptime(last_period_str, "%Y-%m-%d").date()
                    cycle_length = (last_period - previous_period).days

            else:
                error = "Invalid selection."

            # =============================
            # VALIDATION (after assignment)
            # =============================
            if not error:
                if cycle_length < 21 or cycle_length > 35:
                    error = "Cycle length must be between 21 and 35 days."

            # =============================
            # CALCULATION
            # =============================
            if not error:
                ovulation_day = last_period + timedelta(days=cycle_length - 14)
                fertile_start = ovulation_day - timedelta(days=5)
                fertile_end = ovulation_day
                next_period = last_period + timedelta(days=cycle_length)

                results = {
                    "last_period": last_period,
                    "cycle_length": cycle_length,
                    "ovulation_day": ovulation_day,
                    "fertile_start": fertile_start,
                    "fertile_end": fertile_end,
                    "next_period": next_period,
                }

                # =============================
                # SAVE TO DATABASE
                # =============================
                conn = get_db_connection()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO cycles (user_id, last_period, cycle_length)
                    VALUES (%s, %s, %s)
                    """,
                    (session["user_id"], last_period, cycle_length)
                )
                conn.commit()
                cur.close()
                conn.close()

        except ValueError:
            error = "Invalid date or number entered."

    return render_template("dashboard.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)
