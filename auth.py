from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import UserMixin, login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db
import psycopg2

auth_bp = Blueprint("auth", __name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:Mypostgresdb81@localhost:5432/cycle_tracker"
)

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        conn = get_db()
        if not conn:
            return None

        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, username FROM users WHERE id=%s",
                (user_id,)
            )
            user = cur.fetchone()
            return User(*user) if user else None
        except Exception as e:
            print("User fetch error:", e)
            return None
        finally:
            conn.close()


# -------------------------
# REGISTER
# -------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm_password")

        if not username or not password:
            flash("All fields are required", "error")
            return render_template("register.html")

        if password != confirm:
            flash("Passwords do not match", "error")
            return render_template("register.html")

        conn = get_db()
        if not conn:
            flash("Service temporarily unavailable", "error")
            return render_template("register.html")

        try:
            cur = conn.cursor()
            hashed = generate_password_hash(password)
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, hashed)
            )
            conn.commit()
            flash("Account created successfully", "success")
            return redirect(url_for("auth.login"))

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Username already exists", "error")

        except Exception as e:
            conn.rollback()
            print("Registration error:", e)
            flash("Registration failed. Try again.", "error")

        finally:
            conn.close()

    return render_template("register.html")


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        conn = get_db()
        if not conn:
            flash("Service temporarily unavailable", "error")
            return render_template("login.html")

        try:
            cur = conn.cursor()
            cur.execute(
                "SELECT id, password FROM users WHERE username=%s",
                (username,)
            )
            user = cur.fetchone()

            if user and check_password_hash(user[1], password):
                login_user(User(user[0], username))
                return redirect(url_for("dashboard"))

            flash("Invalid username or password", "error")

        except Exception as e:
            print("Login error:", e)
            flash("Login failed. Try again.", "error")

        finally:
            conn.close()

    return render_template("login.html")


# -------------------------
# LOGOUT
# -------------------------
@auth_bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
