import os
import sys

# Test 1: Check paths
print("=" * 50)
print("PATH TEST")
print("=" * 50)
basedir = os.path.abspath(os.path.dirname(__file__))
print(f"basedir: {basedir}")
instance_path = os.path.join(basedir, 'instance')
print(f"instance_path: {instance_path}")
db_path = os.path.join(instance_path, 'mydiary.db')
print(f"db_path: {db_path}")
db_uri = 'sqlite:///' + db_path
print(f"db_uri: {db_uri}")

# Test 2: Create directory
print("\n" + "=" * 50)
print("DIRECTORY CREATION TEST")
print("=" * 50)
try:
    os.makedirs(instance_path, exist_ok=True)
    print(f"✓ Created directory: {instance_path}")
    print(f"✓ Directory exists: {os.path.exists(instance_path)}")
except Exception as e:
    print(f"✗ Error creating directory: {e}")

# Test 3: Test SQLite connection
print("\n" + "=" * 50)
print("SQLITE CONNECTION TEST")
print("=" * 50)
try:
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS test (id INTEGER PRIMARY KEY)")
    conn.commit()
    conn.close()
    print(f"✓ SQLite connection successful")
    print(f"✓ Database file created: {os.path.exists(db_path)}")
except Exception as e:
    print(f"✗ SQLite error: {e}")

print("\n" + "=" * 50)
print("ALL TESTS COMPLETE")
print("=" * 50)
