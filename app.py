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

@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    results = None
    error = None

    if request.method == "POST":
        last_period_str = request.form.get("last_period")
        cycle_length_str = request.form.get("cycle_length")
        next_period_str = request.form.get("next_period")

        if not last_period_str:
            error = "Please enter your last menstrual period."
        else:
            last_period = datetime.strptime(last_period_str, "%Y-%m-%d").date()

            # Case 1: User knows cycle length
            if cycle_length_str:
                try:
                    cycle_length = int(cycle_length_str)
                except ValueError:
                    error = "Cycle length must be a number."
            # Case 2: User does not know cycle length, enter next period
            elif next_period_str:
                try:
                    next_period = datetime.strptime(next_period_str, "%Y-%m-%d").date()
                    cycle_length = (next_period - last_period).days
                except ValueError:
                    error = "Invalid next period date."
            else:
                error = "Please enter either cycle length or next period date."

            # Only calculate if no errors
            if not error:
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
                try:
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
                except Exception as e:
                    flash(f"Error saving to database: {e}", "error")

    return render_template("dashboard.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)
