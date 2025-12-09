import sqlite3
import hashlib
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '../../Phase 2/stock_exchange.db')

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Connect to database
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

print("=" * 60)
print("CHECKING DATABASE USERS")
print("=" * 60)

# Get all users
cursor.execute('SELECT user_id, full_name, email, password, role FROM "User"')
users = cursor.fetchall()

print(f"\nTotal users in database: {len(users)}\n")

for user in users:
    print(f"Email: {user['email']}")
    print(f"Name: {user['full_name']}")
    print(f"Role: {user['role']}")
    print(f"Password hash (first 20 chars): {user['password'][:20]}...")
    print("-" * 40)

print("\n" + "=" * 60)
print("TESTING LOGIN CREDENTIALS")
print("=" * 60)

# Test credentials
test_logins = [
    ('admin@stockex.com', 'admin123'),
    ('demo@stockex.com', 'demo123'),
]

for email, password in test_logins:
    password_hash = hash_password(password)
    print(f"\nTesting: {email} / {password}")
    print(f"Generated hash (first 20 chars): {password_hash[:20]}...")
    
    cursor.execute('SELECT * FROM "User" WHERE email = ? AND password = ?', (email, password_hash))
    result = cursor.fetchone()
    
    if result:
        print(f"✅ LOGIN SUCCESS - Found user: {result['full_name']}")
    else:
        print(f"❌ LOGIN FAILED - No matching user found")
        # Check if email exists but password is wrong
        cursor.execute('SELECT password FROM "User" WHERE email = ?', (email,))
        user_check = cursor.fetchone()
        if user_check:
            print(f"   Email exists but password doesn't match")
            print(f"   Stored hash (first 20 chars): {user_check['password'][:20]}...")
            print(f"   Expected hash (first 20 chars): {password_hash[:20]}...")
        else:
            print(f"   Email not found in database")

conn.close()
