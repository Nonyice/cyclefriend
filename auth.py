import os
import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from flask_login import (
    UserMixin,
    login_user,
    logout_user,
    login_required
)

auth_bp = Blueprint("auth", __name__)


# ---------------- USER MODEL ----------------
class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, username FROM users WHERE id = %s",
            (user_id,)
        )
        row = cur.fetchone()
        cur.close()
        conn.close()

        if row:
            return User(row["id"], row["username"])
        return None


# ---------------- REGISTER ----------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for("auth.register"))

        conn = get_db_connection()
        if not conn:
            flash("Database unavailable", "error")
            return redirect(url_for("auth.register"))

        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO users (username, password) VALUES (%s, %s)",
                (username, generate_password_hash(password))
            )
            conn.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("auth.login"))

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            flash("Username already exists", "error")

        finally:
            cur.close()
            conn.close()

    return render_template("register.html")


# ---------------- LOGIN ----------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "SELECT id, username, password FROM users WHERE username = %s",
            (username,)
        )
        row = cur.fetchone()

        cur.close()
        conn.close()

        if row and check_password_hash(row["password"], password):
            user = User(row["id"], row["username"])
            login_user(user)

            session["user_id"] = user.id  # optional
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password", "error")

    return render_template("login.html")



# ---------------- LOGOUT ----------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("auth.login"))
