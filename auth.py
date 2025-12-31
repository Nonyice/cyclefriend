import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from db import get_db_connection

auth_bp = Blueprint("auth", __name__)

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
        if conn is None:
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
