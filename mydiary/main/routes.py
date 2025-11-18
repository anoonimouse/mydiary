from . import main_bp
from flask import render_template, request, current_app, url_for, redirect, flash
from ..models import User
from ..extensions import db
from flask_login import login_required, current_user
from sqlalchemy import desc

@main_bp.route("/")
def home():
    # Show trending diaries (top by message count)
    trending = User.query.join(User.messages).group_by(User.id).order_by(desc(db.func.count("anonymous_message.id"))).limit(8).all()
    return render_template("home.html", trending=trending)

@main_bp.route("/dashboard")
@login_required
def dashboard():
    # show inbox and stats
    inbox = current_user.messages.order_by(desc("created_at")).limit(50).all()
    entries = current_user.diary_entries.order_by(desc("created_at")).limit(10).all()
    return render_template("dashboard.html", inbox=inbox, entries=entries)
