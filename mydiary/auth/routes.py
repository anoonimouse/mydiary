from . import auth_bp
from flask import render_template, redirect, url_for, flash, request
from ..models import User
from ..extensions import db
from flask_login import login_user, logout_user, current_user, login_required

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if not username or not email or not password:
            flash("Please fill required fields", "danger")
            return render_template("auth/login.html", register=True)
        if User.query.filter_by(username=username).first():
            flash("Username taken", "danger")
            return render_template("auth/login.html", register=True)
        if User.query.filter_by(email=email).first():
            flash("Email already used", "danger")
            return render_template("auth/login.html", register=True)
        u = User(username=username, email=email)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        login_user(u)
        flash("Welcome! Your diary page is ready.", "success")
        return redirect(url_for("main.dashboard"))
    return render_template("auth/login.html", register=True)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.dashboard"))
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("auth/login.html", register=False)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("main.home"))
