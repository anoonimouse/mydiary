from flask import render_template, abort, request, redirect, url_for
from flask_login import login_required, current_user
from mydiary.adminbp import bp
from mydiary.models import User, Message
from mydiary.extensions import db

@bp.route('/')
@login_required
def index():
    # Simple check for admin (in real app, use a role or specific email)
    if current_user.id != 1: # Assuming first user is admin for now
        abort(403)
        
    users = User.query.order_by(User.created_at.desc()).limit(50).all()
    messages_count = Message.query.count()
    flagged_count = Message.query.filter_by(is_flagged=True).count()
    
    return render_template('admin/admin_index.html', 
                         users=users, 
                         messages_count=messages_count,
                         flagged_count=flagged_count)

@bp.route('/flagged')
@login_required
def flagged_messages():
    if current_user.id != 1:
        abort(403)
    
    flagged = Message.query.filter_by(is_flagged=True).order_by(Message.created_at.desc()).all()
    return render_template('admin/flagged.html', messages=flagged)

@bp.route('/message/<int:message_id>/delete', methods=['POST'])
@login_required
def delete_message_admin(message_id):
    if current_user.id != 1:
        abort(403)
    
    message = Message.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    
    return redirect(url_for('adminbp.flagged_messages'))
