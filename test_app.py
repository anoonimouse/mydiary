import os
import sys

print("Python executable:", sys.executable)
print("Current directory:", os.getcwd())
print("Starting import...")

try:
    from mydiary import create_app
    print("Successfully imported create_app")
    
    app = create_app('development')
    print("Successfully created app")
    
    print("App config:")
    print(f"  DEBUG: {app.config.get('DEBUG')}")
    print(f"  DATABASE_URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
    
    # Check if database file was created
    db_path = os.path.join(os.getcwd(), 'instance', 'mydiary.db')
    if os.path.exists(db_path):
        print(f"Database file created at: {db_path}")
    else:
        print(f"Database file NOT found at: {db_path}")
    
    print("\nStarting Flask development server...")
    app.run(debug=True, port=5000)
    
except Exception as e:
    print(f"Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
