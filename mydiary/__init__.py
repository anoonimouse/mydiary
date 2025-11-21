import os
from flask import Flask
from config import config
from mydiary.extensions import db, migrate, login_manager, csrf

def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Ensure instance directory exists
    instance_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'instance')
    os.makedirs(instance_path, exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Register blueprints
    from mydiary.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    from mydiary.main import bp as main_bp
    app.register_blueprint(main_bp)

    from mydiary.diary import bp as diary_bp
    app.register_blueprint(diary_bp)

    from mydiary.inbox import bp as inbox_bp
    app.register_blueprint(inbox_bp)

    from mydiary.adminbp import bp as admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')

    with app.app_context():
        db.create_all()
        # Create admin if not exists
        from mydiary.models import User
        if not User.query.filter_by(username='admin').first():
            admin = User(username='admin', email='admin@mydiary.page', bio='Official Admin Account')
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()

    return app
