import os
from flask import Flask, render_template, redirect, url_for, request
from flask_login import LoginManager, login_required, current_user
from datetime import datetime, timedelta
from dotenv import load_dotenv

from extensions import db
from models import UserAccount, Cycle

load_dotenv()

app = Flask(__name__)

# ─── Config ─────────────────────────────
app.secret_key = os.environ.get("SECRET_KEY", "dev_key")

uri = os.environ.get("DATABASE_URL", "sqlite:///local.db")
if uri.startswith("postgres://"):
    uri = uri.replace("postgres://", "postgresql://", 1)

app.config["SQLALCHEMY_DATABASE_URI"] = uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# ─── Init DB ────────────────────────────
db.init_app(app)

# ─── Login ──────────────────────────────
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

@login_manager.user_loader
def load_user(user_id):
    from auth import User
    return User.get(user_id)

# ─── Blueprint ──────────────────────────
from auth import auth_bp
app.register_blueprint(auth_bp)

@app.before_request
def log():
    print("➡️", request.method, request.path)

# ─── Home ───────────────────────────────
@app.route("/")
def home():
    return redirect(url_for("auth.login"))

# ─── MODE SELECTION ─────────────────────
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
        cycle_length = request.form.get("cycle_length")

        if not last_period or not cycle_length:
            return render_template("known_cycle.html", error="All fields required")

        return redirect(url_for(
            "dashboard",
            last_period=last_period,
            cycle_length=cycle_length
        ))

    return render_template("known_cycle.html")

@app.route("/unknown-cycle", methods=["GET", "POST"])
@login_required
def unknown_cycle():
    if request.method == "POST":
        previous = request.form.get("previous_period")
        last = request.form.get("last_period")

        if not previous or not last:
            return render_template("unknown_cycle.html", error="All fields required")

        try:
            previous_date = datetime.strptime(previous, "%Y-%m-%d").date()
            last_date = datetime.strptime(last, "%Y-%m-%d").date()

            cycle_length = (last_date - previous_date).days

            return redirect(url_for(
                "dashboard",
                last_period=last,
                cycle_length=cycle_length
            ))

        except Exception:
            return render_template("unknown_cycle.html", error="Invalid dates")

    return render_template("unknown_cycle.html")

# ─── DASHBOARD ──────────────────────────
@app.route("/dashboard")
@login_required
def dashboard():
    results = None
    error = None

    last_period = request.args.get("last_period")
    cycle_length = request.args.get("cycle_length")

    if last_period and cycle_length:
        try:
            last_period = datetime.strptime(last_period, "%Y-%m-%d").date()
            cycle_length = int(cycle_length)

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

            # prevent duplicates
            exists = Cycle.query.filter_by(
                user_id=current_user.id,
                last_period=last_period,
                cycle_length=cycle_length
            ).first()

            if not exists:
                db.session.add(Cycle(
                    user_id=current_user.id,
                    last_period=last_period,
                    cycle_length=cycle_length
                ))
                db.session.commit()

        except Exception:
            error = "Invalid data"

    return render_template("dashboard.html", results=results, error=error)

# ─── RUN ────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)