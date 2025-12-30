from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, current_user
import psycopg2, os
from datetime import datetime, timedelta
from auth import auth_bp

app = Flask(__name__)
app.secret_key = "plimsoltech81"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/cycle_tracker"
)


def get_db():
    return psycopg2.connect(DATABASE_URL)

@login_manager.user_loader
def load_user(user_id):
    from auth import User
    return User.get(user_id)

app.register_blueprint(auth_bp)

@app.route("/", methods=["GET", "POST"])
@login_required
def dashboard():
    result = None

    if request.method == "POST":
        last_period = datetime.strptime(request.form["last_period"], "%Y-%m-%d")
        cycle_length = int(request.form["cycle_length"])

        ovulation = last_period + timedelta(days=cycle_length - 14)
        fertile_start = ovulation - timedelta(days=5)
        fertile_end = ovulation + timedelta(days=1)

        result = {
            "next_period": last_period + timedelta(days=cycle_length),
            "fertile_start": fertile_start,
            "fertile_end": fertile_end,
            "ovulation": ovulation
        }

    return render_template("dashboard.html", result=result)

if __name__ == "__main__":
    app.run()

