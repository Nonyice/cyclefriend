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
    fertile_window = []
    peak_day = None

    if request.method == "POST":
        last_period = datetime.strptime(
            request.form["last_period"], "%Y-%m-%d"
        ).date()
        cycle_length = int(request.form["cycle_length"])

        ovulation_day = last_period + timedelta(days=cycle_length - 14)
        fertile_window = [
            ovulation_day - timedelta(days=2),
            ovulation_day - timedelta(days=1),
            ovulation_day,
            ovulation_day + timedelta(days=1),
            ovulation_day + timedelta(days=2),
        ]
        peak_day = ovulation_day

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

    return render_template(
        "dashboard.html",
        fertile_window=fertile_window,
        peak_day=peak_day
    )
if __name__ == "__main__":
    app.run()

