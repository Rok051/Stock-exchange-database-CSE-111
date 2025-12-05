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

print("\n" + "=" * 60)
print("FINDING WORKING CREDENTIALS")
print("=" * 60)

# Get all users
cursor.execute('SELECT email, full_name, role, password FROM "User"')
users = cursor.fetchall()

# Common passwords to try
common_passwords = ['password', 'password123', 'admin', 'admin123', 'demo', 'demo123', '123456', 'test']

working_logins = []

for user in users:
    email = user['email']
    stored_hash = user['password']
    
    for pwd in common_passwords:
        test_hash = hash_password(pwd)
        if test_hash == stored_hash:
            working_logins.append((email, pwd, user['full_name'], user['role']))
            break

print(f"\n✅ WORKING LOGIN CREDENTIALS:\n")
if working_logins:
    for email, password, name, role in working_logins:
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"Name: {name}")
        print(f"Role: {role}")
        print("-" * 40)
else:
    print("❌ No working credentials found with common passwords")
    print("\nAll users in database:")
    for user in users:
        print(f"- {user['email']} ({user['role']}) - Hash: {user['password'][:30]}...")

conn.close()
