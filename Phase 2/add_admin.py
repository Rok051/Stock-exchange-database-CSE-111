import sqlite3

conn = sqlite3.connect('stock_exchange.db')
cursor = conn.cursor()

# Add admin user with password "demo123" (already hashed)
cursor.execute("""
    INSERT INTO User (user_id, full_name, email, password, role) 
    VALUES (lower(hex(randomblob(16))), 'Admin User', 'admin@example.com', 
            'd3ad9315b7be5dd53b31a273b3b3aba5defe700808305aa16a3062b76658a791', 'ADMIN')
""")

conn.commit()
print("✅ Admin user created successfully!")
print("Email: admin@example.com")
print("Password: demo123")
conn.close()
