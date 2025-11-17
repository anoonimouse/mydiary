# ============================================
# app.py - Main Flask Application Entry Point
# ============================================

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_wtf.csrf import CSRFProtect
from flask_caching import Cache
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///mydiary.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['CACHE_TYPE'] = 'simple'  # Use Redis in production
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload

# Initialize extensions
db = SQLAlchemy(app)
csrf = CSRFProtect(app)
cache = Cache(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# ============================================
# models.py - Database Models
# ============================================

from flask_login import UserMixin

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=True)
    theme = db.Column(db.JSON, default={'color': 'purple', 'background': 'gradient'})
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    notes = db.relationship('Note', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Note(db.Model):
    __tablename__ = 'notes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    sender_name = db.Column(db.String(100), nullable=True)
    message = db.Column(db.Text, nullable=False)
    is_anonymous = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='pending', index=True)  # pending, approved, archived, deleted
    reactions = db.Column(db.JSON, default={'heart': 0, 'laugh': 0, 'wow': 0})
    is_private = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<Note {self.id} for User {self.user_id}>'

# ============================================
# Login Manager
# ============================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ============================================
# Utils / Helpers
# ============================================

def sanitize_message(message):
    """Basic XSS protection - sanitize HTML"""
    import html
    return html.escape(message.strip())

def check_profanity(text):
    """Basic profanity filter - extend with better-profanity library"""
    bad_words = ['spam', 'scam']  # Add comprehensive list
    return any(word in text.lower() for word in bad_words)

def get_time_ago(dt):
    """Convert datetime to relative time"""
    now = datetime.utcnow()
    diff = now - dt
    
    if diff.days > 365:
        return f"{diff.days // 365} year{'s' if diff.days // 365 > 1 else ''} ago"
    elif diff.days > 30:
        return f"{diff.days // 30} month{'s' if diff.days // 30 > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        return f"{diff.seconds // 3600} hour{'s' if diff.seconds // 3600 > 1 else ''} ago"
    elif diff.seconds > 60:
        return f"{diff.seconds // 60} minute{'s' if diff.seconds // 60 > 1 else ''} ago"
    else:
        return "Just now"

# ============================================
# Routes - Main Pages
# ============================================

@app.route('/')
def index():
    """Landing page"""
    # Get random diary previews
    preview_users = User.query.limit(6).all()
    return render_template('index.html', preview_users=preview_users)

@app.route('/create', methods=['POST'])
def create_diary():
    """Create new diary"""
    username = request.form.get('username', '').strip().lower()
    
    if not username or len(username) < 3:
        flash('Username must be at least 3 characters', 'error')
        return redirect(url_for('index'))
    
    if User.query.filter_by(username=username).first():
        flash('Username already taken', 'error')
        return redirect(url_for('index'))
    
    # Create new user
    user = User(username=username)
    db.session.add(user)
    db.session.commit()
    
    # Set session cookie
    session['diary_owner'] = user.id
    
    flash(f'Diary created! Share your link: mydiary.page/{username}', 'success')
    return redirect(url_for('diary_page', username=username))

@app.route('/<username>')
@cache.cached(timeout=300, query_string=True)  # Cache for 5 minutes
def diary_page(username):
    """Public diary page"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Get approved notes with pagination
    page = request.args.get('page', 1, type=int)
    notes = Note.query.filter_by(
        user_id=user.id,
        status='approved',
        is_private=False
    ).order_by(Note.created_at.desc()).paginate(
        page=page, per_page=10, error_out=False
    )
    
    # Format notes with time_ago
    for note in notes.items:
        note.time_ago = get_time_ago(note.created_at)
    
    is_owner = session.get('diary_owner') == user.id
    
    return render_template('diary.html', 
                         user=user, 
                         notes=notes,
                         is_owner=is_owner)

@app.route('/<username>/note', methods=['POST'])
def leave_note(username):
    """Submit a new note (HTMX endpoint)"""
    user = User.query.filter_by(username=username).first_or_404()
    
    sender_name = request.form.get('sender_name', '').strip()
    message = request.form.get('message', '').strip()
    is_anonymous = request.form.get('is_anonymous') == 'true'
    is_private = request.form.get('is_private') == 'true'
    
    # Validation
    if not message or len(message) < 5:
        return jsonify({'error': 'Message too short'}), 400
    
    if len(message) > 500:
        return jsonify({'error': 'Message too long (max 500 characters)'}), 400
    
    if check_profanity(message):
        return jsonify({'error': 'Message contains inappropriate content'}), 400
    
    # Sanitize input
    message = sanitize_message(message)
    sender_name = sanitize_message(sender_name) if sender_name else None
    
    # Create note
    note = Note(
        user_id=user.id,
        sender_name=None if is_anonymous else sender_name,
        message=message,
        is_anonymous=is_anonymous,
        is_private=is_private,
        status='pending'
    )
    
    db.session.add(note)
    db.session.commit()
    
    # Clear cache
    cache.delete_memoized(diary_page, username)
    
    return jsonify({
        'success': True,
        'message': 'Note submitted for approval!'
    })

@app.route('/<username>/dashboard')
def dashboard(username):
    """Owner dashboard"""
    user = User.query.filter_by(username=username).first_or_404()
    
    # Check if current session is owner
    if session.get('diary_owner') != user.id:
        flash('Access denied', 'error')
        return redirect(url_for('diary_page', username=username))
    
    # Get notes by status
    pending = Note.query.filter_by(user_id=user.id, status='pending').order_by(Note.created_at.desc()).all()
    approved = Note.query.filter_by(user_id=user.id, status='approved').order_by(Note.created_at.desc()).limit(20).all()
    archived = Note.query.filter_by(user_id=user.id, status='archived').order_by(Note.created_at.desc()).limit(20).all()
    
    # Format time
    for note in pending + approved + archived:
        note.time_ago = get_time_ago(note.created_at)
    
    # Stats
    stats = {
        'total_notes': Note.query.filter_by(user_id=user.id).count(),
        'approved_count': len(approved),
        'pending_count': len(pending),
        'total_reactions': sum(
            sum(note.reactions.values()) 
            for note in Note.query.filter_by(user_id=user.id, status='approved').all()
        )
    }
    
    return render_template('dashboard.html',
                         user=user,
                         pending=pending,
                         approved=approved,
                         archived=archived,
                         stats=stats)

@app.route('/note/<int:note_id>/approve', methods=['POST'])
def approve_note(note_id):
    """Approve a note (HTMX)"""
    note = Note.query.get_or_404(note_id)
    
    if session.get('diary_owner') != note.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    note.status = 'approved'
    db.session.commit()
    
    # Clear cache
    user = User.query.get(note.user_id)
    cache.delete_memoized(diary_page, user.username)
    
    return jsonify({'success': True})

@app.route('/note/<int:note_id>/archive', methods=['POST'])
def archive_note(note_id):
    """Archive a note"""
    note = Note.query.get_or_404(note_id)
    
    if session.get('diary_owner') != note.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    note.status = 'archived'
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/note/<int:note_id>/delete', methods=['POST'])
def delete_note(note_id):
    """Delete a note"""
    note = Note.query.get_or_404(note_id)
    
    if session.get('diary_owner') != note.user_id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    db.session.delete(note)
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/note/<int:note_id>/react', methods=['POST'])
def react_to_note(note_id):
    """Add reaction to note"""
    note = Note.query.get_or_404(note_id)
    reaction_type = request.json.get('type')
    
    if reaction_type not in ['heart', 'laugh', 'wow']:
        return jsonify({'error': 'Invalid reaction'}), 400
    
    # Increment reaction
    reactions = note.reactions or {'heart': 0, 'laugh': 0, 'wow': 0}
    reactions[reaction_type] = reactions.get(reaction_type, 0) + 1
    note.reactions = reactions
    
    db.session.commit()
    
    return jsonify({'success': True, 'reactions': reactions})

@app.route('/discover')
@cache.cached(timeout=300)
def discover():
    """Discover page with trending diaries"""
    # Get users with most approved notes
    trending = db.session.query(
        User,
        db.func.count(Note.id).label('note_count')
    ).join(Note).filter(
        Note.status == 'approved'
    ).group_by(User.id).order_by(
        db.text('note_count DESC')
    ).limit(12).all()
    
    return render_template('discover.html', trending=trending)

@app.route('/search')
def search():
    """Search for diaries"""
    query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify([])
    
    users = User.query.filter(
        User.username.like(f'%{query}%')
    ).limit(10).all()
    
    return jsonify([{
        'username': u.username,
        'url': url_for('diary_page', username=u.username)
    } for u in users])

# ============================================
# Error Handlers
# ============================================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# ============================================
# Template Filters
# ============================================

@app.template_filter('timeago')
def timeago_filter(dt):
    return get_time_ago(dt)

# ============================================
# CLI Commands
# ============================================

@app.cli.command()
def init_db():
    """Initialize the database"""
    db.create_all()
    print('Database initialized!')

@app.cli.command()
def seed_db():
    """Seed database with sample data"""
    # Create sample user
    user = User(username='lovely')
    db.session.add(user)
    db.session.commit()
    
    # Create sample notes
    notes = [
        Note(user_id=user.id, sender_name='Sarah', message='You have the kindest smile!', status='approved'),
        Note(user_id=user.id, message='Thank you for always being there.', is_anonymous=True, status='approved'),
    ]
    
    db.session.bulk_save_objects(notes)
    db.session.commit()
    print('Database seeded!')

# ============================================
# Run Application
# ============================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)