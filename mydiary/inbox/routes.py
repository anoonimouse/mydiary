from . import inbox_bp
from flask import request, redirect, url_for, render_template, current_app, flash, jsonify, abort
from ..models import User, AnonymousMessage
from ..extensions import db
from datetime import datetime, timedelta
from flask import make_response
import hashlib
import time

def ip_hash(ip):
    return hashlib.sha256(ip.encode("utf-8")).hexdigest()

@inbox_bp.route("/<username>/send", methods=["POST"])
def send_message(username):
    user = User.query.filter_by(username=username).first_or_404()
    content = request.form.get("content", "").strip()
    category = request.form.get("category", "general")
    if not content:
        return ("", 400)
    # basic rate limit by cookie timestamp
    last = request.cookies.get(f"last_msg_{user.id}")
    now = int(time.time())
    rate_seconds = current_app.config.get("MESSAGE_RATE_LIMIT_SECONDS", 10)
    if last and now - int(last) < rate_seconds:
        return ("", 429)
    m = AnonymousMessage(to_user_id=user.id, content=content, category=category)
    # store hashed IP (if present) — basic privacy-first hash
    ip = request.remote_addr or "0.0.0.0"
    m.ip_hash = ip_hash(ip)
    db.session.add(m)
    db.session.commit()
    resp = make_response(render_template("components/message_card.html", msg=m))
    resp.set_cookie(f"last_msg_{user.id}", str(now), max_age=60*60*24)
    return resp

@inbox_bp.route("/messages/<int:msg_id>/toggle_read", methods=["POST"])
def toggle_read(msg_id):
    m = AnonymousMessage.query.get_or_404(msg_id)
    m.is_read = not m.is_read
    db.session.commit()
    return ("", 204)

@inbox_bp.route("/messages/<int:msg_id>/flag", methods=["POST"])
def flag_message(msg_id):
    m = AnonymousMessage.query.get_or_404(msg_id)
    m.flagged = True
    db.session.commit()
    return ("", 204)
