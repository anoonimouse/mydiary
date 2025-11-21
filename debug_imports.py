with open('debug_log.txt', 'w') as f:
    f.write("Start\n")
    try:
        f.write("Importing create_app\n")
        from mydiary import create_app
        f.write("Imported create_app\n")
        
        f.write("Creating app\n")
        app = create_app('development')
        f.write("Created app\n")
        
        f.write("Importing db\n")
        from mydiary.extensions import db
        f.write("Imported db\n")
        
        with app.app_context():
            f.write("Creating all\n")
            db.create_all()
            f.write("Created all\n")

    except Exception as e:
        f.write(f"Error: {e}\n")
    f.write("End\n")
