# mydiary.page 💖

A Gen-Z anonymous messaging diary app. Real friends, real fun.

## Features
- 📝 **Personal Diary Page**: Create your own aesthetic page.
- 💌 **Anonymous Messaging**: Receive confessions, roasts, and more.
- 🎨 **Custom Themes**: Express your vibe.
- 🔒 **Safety First**: AI moderation and blocking tools.
- 📱 **Mobile First**: Designed for the scroll generation.

## Tech Stack
- **Backend**: Flask, SQLAlchemy, Flask-Login
- **Frontend**: TailwindCSS, Alpine.js, HTMX
- **Database**: SQLite (Dev) / PostgreSQL (Prod)

## Setup & Run

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize Database**
   ```bash
   python setup_db.py
   ```
   *Or use Flask CLI:*
   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

3. **Run the App**
   ```bash
   python run.py
   ```
   Access at `http://localhost:5000`

## Admin Access
- **Username**: admin
- **Password**: admin123
- **URL**: `/admin`

## Project Structure
- `mydiary/`: Core application package
  - `auth/`: Authentication routes
  - `main/`: Public pages (Home, About, Blog)
  - `diary/`: User dashboard & profile
  - `inbox/`: Messaging logic
  - `templates/`: HTML templates
  - `static/`: CSS, JS, Images
- `instance/`: Database file (created after init)
