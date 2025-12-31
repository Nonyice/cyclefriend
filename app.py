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
        try:
            # Option 1: User knows cycle length
            last_period_str = request.form.get("last_period_known")
            cycle_length_str = request.form.get("cycle_length")
            
            if last_period_str and cycle_length_str:
                last_period = datetime.strptime(last_period_str, "%Y-%m-%d").date()
                cycle_length = int(cycle_length_str)

            # Option 2: User does NOT know cycle length
            else:
                prev_period_str = request.form.get("previous_period")
                last_period_str = request.form.get("last_period_unknown")

                if prev_period_str and last_period_str:
                    previous_period = datetime.strptime(prev_period_str, "%Y-%m-%d").date()
                    last_period = datetime.strptime(last_period_str, "%Y-%m-%d").date()
                    cycle_length = (last_period - previous_period).days
                else:
                    error = "Please fill either Option 1 or Option 2 completely."
                    return render_template("dashboard.html", results=None, error=error)
                    if not (21 <= cycle_length <= 35):
                        error = "Computed cycle length is unrealistic (21-35 days). Please check your dates."
                        return render_template("dashboard.html", results=None, error=error)


            # Compute results
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

        except ValueError:
            error = "Invalid date or cycle length."

    return render_template("dashboard.html", results=results, error=error)

if __name__ == "__main__":
    app.run(debug=True)
