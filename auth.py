from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2, os

auth_bp = Blueprint("auth", __name__)@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            return render_template(
                "register.html",
                error="Passwords do not match"
            )

        hashed = generate_password_hash(password)

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, hashed)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("auth.login"))

    return render_template("register.html")


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@localhost:5432/cycle_tracker"
)


def get_db():
    return psycopg2.connect(DATABASE_URL)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        conn = get_db()
        cur = conn.cursor()
        cur.execute("SELECT id, username FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        conn.close()
        return User(*user) if user else None

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = generate_password_hash(request.form["password"])

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password) VALUES (%s, %s)",
            (username, password)
        )
        conn.commit()
        conn.close()
        return redirect(url_for("auth.login"))

    return render_template("register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password FROM users WHERE username=%s",
            (username,)
        )
        user = cur.fetchone()
        conn.close()

        if user and check_password_hash(user[1], password):
            login_user(User(user[0], username))
            return redirect(url_for("dashboard"))

    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))

