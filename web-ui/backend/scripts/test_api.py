import requests
import json

BASE_URL = 'http://localhost:5001/api'

# 1. Login
print("Logging in...")
try:
    response = requests.post(f'{BASE_URL}/auth/login', json={
        'email': 'demo@stockex.com',
        'password': 'demo123'
    })
    
    if response.status_code != 200:
        print(f"Login failed: {response.text}")
        exit(1)
        
    data = response.json()
    token = data['token']
    user_id = data['user']['user_id']
    print(f"Login successful. User ID: {user_id}")
    
    # 2. Get Portfolio Summary
    headers = {'Authorization': f'Bearer {token}'}
    print(f"\nFetching portfolio summary for user {user_id}...")
    response = requests.get(f'{BASE_URL}/users/{user_id}/portfolio-summary', headers=headers)
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    # 3. Get Accounts
    print(f"\nFetching accounts for user {user_id}...")
    response = requests.get(f'{BASE_URL}/users/{user_id}/accounts', headers=headers)
    print(f"Accounts found: {len(response.json())}")

except Exception as e:
    print(f"Error: {e}")
