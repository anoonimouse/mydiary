from flask import render_template, redirect, url_for, flash, request, abort, jsonify
from flask_login import login_required, current_user
from mydiary.extensions import db
from mydiary.diary import bp
from mydiary.models import User, DiaryEntry, Message

@bp.route('/dashboard')
@login_required
def dashboard():
    messages = Message.query.filter_by(recipient_id=current_user.id).order_by(Message.created_at.desc()).all()
    entries = DiaryEntry.query.filter_by(user_id=current_user.id).order_by(DiaryEntry.created_at.desc()).all()
    return render_template('dashboard.html', messages=messages, entries=entries)

@bp.route('/<username>')
def public_profile(username):
    user = User.query.filter_by(username=username).first()
    
    # Redirect to homepage if user not found
    if not user:
        flash('User not found. Create your own page!', 'info')
        return redirect(url_for('main.index'))
    
    entries = user.entries.filter_by(is_public=True).order_by(DiaryEntry.created_at.desc()).all()
    return render_template('profile.html', user=user, entries=entries)

@bp.route('/diary/new', methods=['POST'])
@login_required
def create_diary_entry():
    content = request.form.get('content')
    is_public = request.form.get('is_public') == 'true'
    
    if not content:
        return '<div class="text-red-500">Content cannot be empty!</div>', 400
    
    entry = DiaryEntry(
        user_id=current_user.id,
        content=content,
        is_public=is_public
    )
    db.session.add(entry)
    db.session.commit()
    
    # Return the new entry HTML
    return f'''
    <div class="bg-white/5 border border-white/10 p-6 rounded-3xl mb-4" id="entry-{entry.id}">
        <div class="flex justify-between items-start mb-3">
            <span class="text-gray-400 text-sm">{entry.created_at.strftime('%b %d, %Y at %H:%M')}</span>
            <span class="px-3 py-1 rounded-full text-xs font-bold {'bg-green-500/20 text-green-400' if entry.is_public else 'bg-gray-500/20 text-gray-400'}">
                {'Public' if entry.is_public else 'Private'}
            </span>
        </div>
        <p class="text-white text-lg mb-4">{entry.content}</p>
        <div class="flex gap-2">
            <button hx-post="/diary/{entry.id}/toggle-public" hx-swap="outerHTML" hx-target="#entry-{entry.id}"
                class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-sm transition-colors">
                {'Make Private' if entry.is_public else 'Make Public'}
            </button>
            <button hx-delete="/diary/{entry.id}" hx-confirm="Delete this entry?" hx-swap="outerHTML" hx-target="#entry-{entry.id}"
                class="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl text-sm transition-colors">
                Delete
            </button>
        </div>
    </div>
    '''

@bp.route('/diary/<int:entry_id>/toggle-public', methods=['POST'])
@login_required
def toggle_diary_public(entry_id):
    entry = DiaryEntry.query.get_or_404(entry_id)
    
    if entry.user_id != current_user.id:
        abort(403)
    
    entry.is_public = not entry.is_public
    db.session.commit()
    
    # Return updated entry HTML
    return f'''
    <div class="bg-white/5 border border-white/10 p-6 rounded-3xl mb-4" id="entry-{entry.id}">
        <div class="flex justify-between items-start mb-3">
            <span class="text-gray-400 text-sm">{entry.created_at.strftime('%b %d, %Y at %H:%M')}</span>
            <span class="px-3 py-1 rounded-full text-xs font-bold {'bg-green-500/20 text-green-400' if entry.is_public else 'bg-gray-500/20 text-gray-400'}">
                {'Public' if entry.is_public else 'Private'}
            </span>
        </div>
        <p class="text-white text-lg mb-4">{entry.content}</p>
        <div class="flex gap-2">
            <button hx-post="/diary/{entry.id}/toggle-public" hx-swap="outerHTML" hx-target="#entry-{entry.id}"
                class="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-xl text-sm transition-colors">
                {'Make Private' if entry.is_public else 'Make Public'}
            </button>
            <button hx-delete="/diary/{entry.id}" hx-confirm="Delete this entry?" hx-swap="outerHTML" hx-target="#entry-{entry.id}"
                class="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-xl text-sm transition-colors">
                Delete
            </button>
        </div>
    </div>
    '''

@bp.route('/diary/<int:entry_id>', methods=['DELETE'])
@login_required
def delete_diary_entry(entry_id):
    entry = DiaryEntry.query.get_or_404(entry_id)
    
    if entry.user_id != current_user.id:
        abort(403)
    
    db.session.delete(entry)
    db.session.commit()
    
    return '', 200

@bp.route('/settings/theme', methods=['POST'])
@login_required
def update_theme():
    theme = request.form.get('theme')
    
    if theme not in ['default', 'bubblegum', 'vaporwave', 'cyberpop', 'soft-girl']:
        return 'Invalid theme', 400
    
    current_user.theme_preference = theme
    db.session.commit()
    
    return f'<div class="text-green-400 text-sm">✓ Theme updated to {theme}!</div>'

@bp.route('/settings/profile', methods=['POST'])
@login_required
def update_profile():
    bio = request.form.get('bio', '').strip()
    
    if len(bio) > 140:
        return '<div class="text-red-400 text-sm">Bio must be 140 characters or less</div>', 400
    
    current_user.bio = bio
    db.session.commit()
    
    return '<div class="text-green-400 text-sm">✓ Profile updated!</div>'
