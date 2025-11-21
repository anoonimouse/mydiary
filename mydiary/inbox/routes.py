from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from mydiary.extensions import db
from mydiary.inbox import bp
from mydiary.models import User, Message

@bp.route('/send/<username>', methods=['POST'])
def send_message(username):
    user = User.query.filter_by(username=username).first_or_404()
    content = request.form.get('content')
    category = request.form.get('category', 'text')
    
    if not content:
        return '<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative">Message cannot be empty!</div>'

    # Rate limiting could go here (check IP)
    
    msg = Message(
        recipient_id=user.id,
        content=content,
        category=category,
        sender_ip=request.remote_addr
    )
    db.session.add(msg)
    db.session.commit()
    
    return f'''
    <div class="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative text-center">
        <strong class="font-bold">Sent! 🚀</strong>
        <span class="block sm:inline">Your anonymous message has been delivered.</span>
        <button onclick="location.reload()" class="mt-2 bg-green-500 text-white font-bold py-1 px-3 rounded text-sm">Send Another</button>
    </div>
    '''

@bp.route('/message/<int:message_id>/flag', methods=['POST'])
@login_required
def flag_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.recipient_id != current_user.id:
        abort(403)
    
    message.is_flagged = not message.is_flagged
    db.session.commit()
    
    status_text = '🚩 Flagged' if message.is_flagged else '✓ Unflagged'
    return f'<div class="text-yellow-400 text-sm">{status_text}</div>'

@bp.route('/message/<int:message_id>/read', methods=['POST'])
@login_required
def mark_read(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.recipient_id != current_user.id:
        abort(403)
    
    message.is_read = True
    db.session.commit()
    
    return '', 200

@bp.route('/message/<int:message_id>', methods=['DELETE'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    if message.recipient_id != current_user.id:
        abort(403)
    
    db.session.delete(message)
    db.session.commit()
    
    return '', 200
