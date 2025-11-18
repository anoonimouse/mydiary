from . import diary_bp
from flask import render_template, request, abort, flash, redirect, url_for
from ..models import User, DiaryEntry
from ..extensions import db
from flask_login import current_user, login_required

@diary_bp.route("/<username>", methods=["GET"])
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    # Show public diary entries and the send-message widget
    public_entries = user.diary_entries.filter_by(public=True).order_by(DiaryEntry.created_at.desc()).limit(20).all()
    return render_template("profile.html", user=user, entries=public_entries)

@diary_bp.route("/<username>/post", methods=["POST"])
@login_required
def new_post(username):
    if current_user.username != username:
        abort(403)
    title = request.form.get("title", "")
    body = request.form.get("body", "")
    public = bool(request.form.get("public"))
    e = DiaryEntry(user_id=current_user.id, title=title, body=body, public=public)
    db.session.add(e)
    db.session.commit()
    flash("Posted", "success")
    return redirect(url_for("diary.profile", username=username))
