from . import admin_bp
from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_required
from ..models import User, AnonymousMessage
from ..extensions import db

@admin_bp.route("/")
@login_required
def index():
    if not current_user.is_admin:
        flash("Admin only", "danger")
        return redirect(url_for("main.home"))
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    flagged = AnonymousMessage.query.filter_by(flagged=True).order_by(AnonymousMessage.created_at.desc()).limit(50).all()
    return render_template("admin/admin_index.html", users=users, flagged=flagged)
