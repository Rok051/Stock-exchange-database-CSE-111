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
    # 1. Create Admin User
    admin_id = uuid.uuid4().hex
    admin_pass = hash_password('admin123')
    cursor.execute("""
        INSERT INTO User (user_id, full_name, email, password, role)
        VALUES (?, 'System Administrator', 'admin@stockex.com', ?, 'ADMIN')
    """, (admin_id, admin_pass))
    print("✅ Admin user created: admin@stockex.com / admin123")

    # 2. Create Demo User
    demo_id = 'user001' # Fixed ID for consistency with populate script if needed, or random
    # populate_demo_data.py looks up by email, so ID doesn't strictly matter, but let's use a fixed one for easier debugging
    demo_pass = hash_password('demo123')
    cursor.execute("""
        INSERT INTO User (user_id, full_name, email, password, role)
        VALUES (?, 'Demo User', 'demo@stockex.com', ?, 'USER')
    """, (demo_id, demo_pass))
    print("✅ Demo user created: demo@stockex.com / demo123")
    
    conn.commit()

except sqlite3.IntegrityError as e:
    print(f"⚠️ Users might already exist: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    conn.close()
