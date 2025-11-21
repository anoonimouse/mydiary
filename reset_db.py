from mydiary import create_app, db

app = create_app('development')

with app.app_context():
    print("Dropping all tables...")
    db.drop_all()
    print("Tables dropped. Run 'python run.py' to recreate them with the new schema.")
