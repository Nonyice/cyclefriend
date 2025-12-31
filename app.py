from flask import Flask, render_template, redirect, url_for, request, session
from flask_login import LoginManager, login_required, current_user
import psycopg2, os
from datetime import datetime, timedelta
from auth import auth_bp
from datetime import datetime, timedelta
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

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    results = None

    if request.method == "POST":
        last_period_str = request.form.get("last_period")
        cycle_length_str = request.form.get("cycle_length")
        next_period_str = request.form.get("next_period")

        last_period = datetime.strptime(last_period_str, "%Y-%m-%d").date()

        # CASE 1: User knows cycle length
        if cycle_length_str:
            cycle_length = int(cycle_length_str)

        # CASE 2: User does NOT know cycle length
        elif next_period_str:
            next_period = datetime.strptime(next_period_str, "%Y-%m-%d").date()
            cycle_length = (next_period - last_period).days

        else:
            return render_template(
                "dashboard.html",
                error="Please provide cycle length or next period date."
            )

        # Calculations
        ovulation_day = last_period + timedelta(days=cycle_length - 14)
        fertile_start = ovulation_day - timedelta(days=5)
        fertile_end = ovulation_day
        predicted_next_period = last_period + timedelta(days=cycle_length)

        results = {
            "last_period": last_period,
            "cycle_length": cycle_length,
            "ovulation_day": ovulation_day,
            "fertile_start": fertile_start,
            "fertile_end": fertile_end,
            "next_period": predicted_next_period,
        }

        # Save to DB
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

    return render_template("dashboard.html", results=results)

if __name__ == "__main__":
    app.run()

