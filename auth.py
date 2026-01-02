import os
import psycopg2
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection
from flask_login import logout_user, login_required
from flask import redirect, url_for, flash



auth_bp = Blueprint("auth", __name__)

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
        if not conn:
            flash("Database unavailable", "error")
            return redirect(url_for("auth.login"))

        cur = conn.cursor()
        cur.execute(
            "SELECT id, password FROM users WHERE username = %s",
            (username,)
        )
        user = cur.fetchone()
        cur.close()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password", "error")
    return render_template("login.html")
    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        flash("Login successful", "success")
        return redirect(url_for("dashboard"))






@auth_bp.route("/logout")
def logout():
    logout_user()          # Flask-Login logout
    session.clear()        # Clear session data
    return redirect(url_for("auth.login"))

