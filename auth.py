from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, logout_user, login_required
from sqlalchemy.exc import IntegrityError

from extensions import db
from models import UserAccount

auth_bp = Blueprint("auth", __name__)


class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

    @staticmethod
    def get(user_id):
        row = UserAccount.query.get(int(user_id))
        if row:
            return User(row.id, row.username)
        return None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        confirm  = request.form["confirm_password"]

        if password != confirm:
            flash("Passwords do not match", "error")
            return redirect(url_for("auth.register"))

        new_user = UserAccount(
            username=username,
            password=generate_password_hash(password)
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("auth.login"))
        except IntegrityError:
            db.session.rollback()
            flash("Username already exists", "error")
            return redirect(url_for("auth.register"))

    return render_template("register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        row = UserAccount.query.filter_by(username=username).first()

        if row and check_password_hash(row.password, password):
            user = User(row.id, row.username)
            login_user(user)
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password", "error")

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have logged out.", "success")
    return redirect(url_for("auth.login"))