import os
from mydiary import create_app
from mydiary.extensions import db

# Print debug info
print("Current working directory:", os.getcwd())
print("Script location:", os.path.abspath(__file__))

app = create_app('development')

with app.app_context():
    print("Database URI:", app.config['SQLALCHEMY_DATABASE_URI'])
    print("Creating tables...")
    db.create_all()
    print("Database tables created successfully!")
    
    from mydiary.models import User
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', email='admin@mydiary.page', bio='Official Admin Account')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("Admin user created.")
    else:
        print("Admin user already exists.")
