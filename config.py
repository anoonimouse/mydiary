import os
from dotenv import load_dotenv
load_dotenv()

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY") or "dev-secret-key"
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or \
        "sqlite:///" + os.path.join(basedir, "instance", "mydiary.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_TIME_LIMIT = None
    # Admin account defaults (only for dev initial setup)
    ADMIN_EMAIL = os.environ.get("ADMIN_EMAIL") or "admin@mydiary.page"
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD") or "changeme"
    # Rate limits and anti-spam (simple)
    MESSAGE_RATE_LIMIT_SECONDS = int(os.environ.get("MESSAGE_RATE_LIMIT_SECONDS") or 10)
