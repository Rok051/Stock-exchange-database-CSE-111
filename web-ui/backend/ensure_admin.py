import sqlite3
import os
import hashlib
import uuid

# Connect to database  
DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

try:
    # Check if admin exists
    cursor.execute("SELECT user_id FROM User WHERE email = 'admin@stockex.com'")
    admin = cursor.fetchone()
    
    if not admin:
        print("Creating admin user...")
        user_id = uuid.uuid4().hex
        password_hash = hash_password('admin123')
        cursor.execute("""
            INSERT INTO User (user_id, full_name, email, password, role)
            VALUES (?, 'System Administrator', 'admin@stockex.com', ?, 'ADMIN')
        """, (user_id, password_hash))
        conn.commit()
        print("✅ Admin user created: admin@stockex.com / admin123")
    else:
        print("ℹ️ Admin user already exists")
        
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.close()
