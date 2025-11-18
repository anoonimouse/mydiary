from flask import Flask
from .extensions import db, login_manager, migrate, admin as flask_admin
from .config import Config
from .models import User, DiaryEntry, AnonymousMessage
import os

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    # ensure instance folder exists
    try:
        os.makedirs(app.instance_path, exist_ok=True)
    except OSError:
        pass

    # init extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    # Import Blueprints
    from .auth.routes import auth_bp
    from .main.routes import main_bp
    from .diary.routes import diary_bp
    from .inbox.routes import inbox_bp
    from .adminbp.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(diary_bp)
    app.register_blueprint(inbox_bp)
    app.register_blueprint(admin_bp, url_prefix="/admin")

    # Flask-Admin - simple admin view
    from flask_admin import Admin
    from flask_admin.contrib.sqla import ModelView
    admin = Admin(app, name="mydiary-admin", template_mode="bootstrap4")
    admin.add_view(ModelView(User, db.session))
    admin.add_view(ModelView(DiaryEntry, db.session))
    admin.add_view(ModelView(AnonymousMessage, db.session))

    # create admin user if not exists (dev convenience)
    @app.before_first_request
    def create_default_admin():
        from .models import User
        if not User.query.filter_by(email=app.config['ADMIN_EMAIL']).first():
            u = User.create_admin(email=app.config['ADMIN_EMAIL'],
                                  password=app.config['ADMIN_PASSWORD'],
                                  username="admin")
            db.session.add(u)
            db.session.commit()

    return app
