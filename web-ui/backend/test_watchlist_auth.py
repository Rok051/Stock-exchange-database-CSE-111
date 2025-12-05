"""
Test watchlist creation for regular user
"""
import requests

BASE_URL = "http://localhost:5001/api"

# Step 1: Login as regular user (Rohit)
print("=" * 60)
print("Testing Watchlist Creation for Regular User")
print("=" * 60)

login_response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "rohit@example.com",
    "password": "demo123"
})

if login_response.status_code == 200:
    token = login_response.json()['token']
    user = login_response.json()['user']
    print(f"✅ Logged in as: {user['full_name']} ({user['role']})")
    print(f"   Token: {token[:20]}...")
    
    # Step 2: Try to create a watchlist
    headers = {"Authorization": f"Bearer {token}"}
    
    watchlist_data = {
        "name": "My Tech Stocks"
    }
    
    create_response = requests.post(
        f"{BASE_URL}/watchlists",
        json=watchlist_data,
        headers=headers
    )
    
    print(f"\n📝 Creating watchlist...")
    print(f"   Status Code: {create_response.status_code}")
    print(f"   Response: {create_response.json()}")
    
    if create_response.status_code == 201:
        print("✅ SUCCESS: Watchlist created!")
        watchlist_id = create_response.json()['watchlist_id']
        
        # Step 3: Try to get all watchlists
        get_response = requests.get(f"{BASE_URL}/watchlists", headers=headers)
        print(f"\n📋 Getting user's watchlists...")
        print(f"   Status Code: {get_response.status_code}")
        if get_response.status_code == 200:
            watchlists = get_response.json()
            print(f"   Found {len(watchlists)} watchlist(s)")
            for wl in watchlists:
                print(f"   - {wl['name']} (ID: {wl['watchlist_id'][:8]}...)")
        
        # Step 4: Try to delete the watchlist
        delete_response = requests.delete(
            f"{BASE_URL}/watchlists/{watchlist_id}",
            headers=headers
        )
        print(f"\n🗑️  Deleting watchlist...")
        print(f"   Status Code: {delete_response.status_code}")
        print(f"   Response: {delete_response.json()}")
        
        if delete_response.status_code == 200:
            print("✅ SUCCESS: Watchlist deleted!")
        else:
            print("❌ FAILED to delete watchlist")
    else:
        print("❌ FAILED to create watchlist")
        
else:
    print(f"❌ Login failed: {login_response.json()}")

print("\n" + "=" * 60)
