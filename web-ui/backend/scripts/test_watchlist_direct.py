import requests

# Login first to get a token
login_response = requests.post("http://localhost:5001/api/auth/login", json={
    "email": "rohit@example.com",
    "password": "demo123"
})

print("Login Response:", login_response.status_code)
if login_response.status_code == 200:
    token = login_response.json()['token']
    user = login_response.json()['user']
    print(f"Logged in as: {user['full_name']} ({user['role']})")
    print(f"Token: {token[:20]}...")
    
    # Try to create a watchlist
    headers = {"Authorization": f"Bearer {token}"}
    watchlist_data = {"name": "Direct API Test Watchlist"}
    
    create_response = requests.post(
        "http://localhost:5001/api/watchlists",
        json=watchlist_data,
        headers=headers
    )
    
    print(f"\nCreate Watchlist Response: {create_response.status_code}")
    print(f"Response Body: {create_response.json()}")
    
    if create_response.status_code == 201:
        print("✅ SUCCESS - Watchlist created via API!")
    else:
        print("❌ FAILED - Check the error above")
else:
    print("Login failed:", login_response.json())
