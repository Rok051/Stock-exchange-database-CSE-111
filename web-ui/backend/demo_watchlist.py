import requests
import time

BASE_URL = "http://localhost:5001/api"

print("=" * 60)
print("WATCHLIST CREATION DEMO - Testing as Regular User (Rohit)")
print("=" * 60)

# Step 1: Login
print("\n[Step 1] Logging in as rohit@example.com...")
response = requests.post(f"{BASE_URL}/auth/login", json={
    "email": "rohit@example.com",
    "password": "demo123"
})

if response.status_code != 200:
    print(f"❌ Login failed: {response.status_code}")
    exit(1)

data = response.json()
token = data['token']
user = data['user']
print(f"✅ Logged in successfully!")
print(f"   User: {user['full_name']}")
print(f"   Role: {user['role']}")

headers = {"Authorization": f"Bearer {token}"}

# Step 2: Get current watchlists
print("\n[Step 2] Getting current watchlists...")
response = requests.get(f"{BASE_URL}/watchlists", headers=headers)

if response.status_code != 200:
    print(f"❌ Failed to get watchlists: {response.status_code}")
    exit(1)

watchlists_before = response.json()
print(f"✅ Current watchlists: {len(watchlists_before)}")
for wl in watchlists_before:
    print(f"   - {wl['name']} ({wl['item_count']} items)")

# Step 3: Create new watchlist
timestamp = time.strftime("%H:%M:%S")
watchlist_name = f"Demo Test {timestamp}"

print(f"\n[Step 3] Creating new watchlist: '{watchlist_name}'...")
response = requests.post(
    f"{BASE_URL}/watchlists",
    json={"name": watchlist_name},
    headers=headers
)

if response.status_code != 201:
    print(f"❌ Failed to create watchlist!")
    print(f"   Status Code: {response.status_code}")
    print(f"   Response: {response.text}")
    exit(1)

created_data = response.json()
new_watchlist_id = created_data['watchlist_id']
print(f"✅ Watchlist created successfully!")
print(f"   Watchlist ID: {new_watchlist_id[:16]}...")

# Step 4: Verify it was added
print(f"\n[Step 4] Verifying watchlist was added...")
response = requests.get(f"{BASE_URL}/watchlists", headers=headers)

if response.status_code != 200:
    print(f"❌ Failed to verify: {response.status_code}")
    exit(1)

watchlists_after = response.json()
print(f"✅ Now have {len(watchlists_after)} watchlists!")

# Find the one we just created
new_watchlist = next((w for w in watchlists_after if w['watchlist_id'] == new_watchlist_id), None)

if new_watchlist:
    print(f"✅ Found our new watchlist:")
    print(f"   Name: {new_watchlist['name']}")
    print(f"   Owner: {new_watchlist['full_name']}")
    print(f"   Items: {new_watchlist['item_count']}")
else:
    print(f"❌ Could not find the watchlist we just created!")
    exit(1)

# Step 5: View details
print(f"\n[Step 5] Getting watchlist details...")
response = requests.get(f"{BASE_URL}/watchlists/{new_watchlist_id}", headers=headers)

if response.status_code != 200:
    print(f"❌ Failed to get details: {response.status_code}")
    exit(1)

details = response.json()
print(f"✅ Watchlist details:")
print(f"   Name: {details['name']}")
print(f"   Items: {len(details.get('items', []))}")

# Final Summary
print("\n" + "=" * 60)
print("✅ ALL TESTS PASSED!")
print("=" * 60)
print("\nSUMMARY:")
print(f"  • Logged in as regular user (Rohit)")
print(f"  • Retrieved {len(watchlists_before)} existing watchlists")
print(f"  • Created new watchlist: '{watchlist_name}'")
print(f"  • Verified creation (now {len(watchlists_after)} total)")
print(f"  • Viewed watchlist details successfully")
print(f"\n🎉 Watchlist feature is WORKING for regular users!")
print("   No admin errors, no permissions issues!")
print("=" * 60)
