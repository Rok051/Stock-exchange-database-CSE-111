"""
Test script for automated order fulfillment
Tests BUY/SELL orders, holdings updates, and cash balance changes
"""
import requests
import json

BASE_URL = "http://localhost:5001/api"

def print_test_header(test_name):
    print("\n" + "=" * 60)
    print(f"TEST: {test_name}")
    print("=" * 60)

def print_result(success, message):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

# Test 1: Create a test account with cash
print_test_header("Setup: Create Test Account")
test_account_data = {
    "user_id": "user001",  # Use existing demo user
    "name": "Test Trading Account",
    "cash_balance": 10000.0,
    "status": "ACTIVE"
}

response = requests.post(f"{BASE_URL}/accounts", json=test_account_data)
if response.status_code == 201:
    account_id = response.json()['account_id']
    print_result(True, f"Created account {account_id} with $10,000")
else:
    print_result(False, f"Failed to create account: {response.text}")
    exit(1)

# Get a security to trade
print_test_header("Setup: Get Security to Trade")
response = requests.get(f"{BASE_URL}/securities")
if response.status_code == 200:
    securities = response.json()
    if securities:
        security = securities[0]
        security_id = security['security_id']
        ticker = security['ticker']
        print_result(True, f"Using security: {ticker} (ID: {security_id})")
    else:
        print_result(False, "No securities found in database")
        exit(1)
else:
    print_result(False, "Failed to get securities")
    exit(1)

# Test 2: Create and fill a BUY order
print_test_header("Test 1: BUY Order - Initial Purchase")
buy_order_1 = {
    "account_id": account_id,
    "security_id": security_id,
    "side": "BUY",
    "type": "LIMIT",
    "quantity": 100,
    "limit_price": 50.0
}

response = requests.post(f"{BASE_URL}/orders", json=buy_order_1)
if response.status_code == 201:
    order_id_1 = response.json()['order_id']
    print_result(True, f"Created BUY order for 100 shares at $50")
    
    # Fill the order
    response = requests.put(f"{BASE_URL}/orders/{order_id_1}/status", json={"status": "FILLED"})
    if response.status_code == 200:
        print_result(True, f"Order filled: {response.json()['details']}")
        
        # Verify holdings
        response = requests.get(f"{BASE_URL}/accounts/{account_id}/holdings")
        holdings = response.json()
        if holdings:
            holding = holdings[0]
            expected_qty = 100
            expected_avg = 50.0
            qty_match = holding['quantity'] == expected_qty
            avg_match = abs(holding['avg_cost'] - expected_avg) < 0.01
            
            print_result(qty_match, f"Holdings quantity: {holding['quantity']} (expected: {expected_qty})")
            print_result(avg_match, f"Average cost: ${holding['avg_cost']:.2f} (expected: ${expected_avg:.2f})")
        else:
            print_result(False, "No holdings found after BUY")
        
        # Verify cash balance
        response = requests.get(f"{BASE_URL}/accounts/{account_id}")
        account = response.json()
        expected_balance = 10000 - (100 * 50)
        balance_match = abs(account['cash_balance'] - expected_balance) < 0.01
        print_result(balance_match, f"Cash balance: ${account['cash_balance']:.2f} (expected: ${expected_balance:.2f})")
    else:
        print_result(False, f"Failed to fill order: {response.text}")
else:
    print_result(False, f"Failed to create order: {response.text}")

# Test 3: Second BUY order - Test average cost calculation
print_test_header("Test 2: BUY Order - Average Cost Calculation")
buy_order_2 = {
    "account_id": account_id,
    "security_id": security_id,
    "side": "BUY",
    "type": "LIMIT",
    "quantity": 50,
    "limit_price": 60.0
}

response = requests.post(f"{BASE_URL}/orders", json=buy_order_2)
if response.status_code == 201:
    order_id_2 = response.json()['order_id']
    print_result(True, f"Created BUY order for 50 shares at $60")
    
    response = requests.put(f"{BASE_URL}/orders/{order_id_2}/status", json={"status": "FILLED"})
    if response.status_code == 200:
        print_result(True, f"Order filled: {response.json()['details']}")
        
        # Verify holdings - should be 150 shares at avg cost of ~$53.33
        response = requests.get(f"{BASE_URL}/accounts/{account_id}/holdings")
        holdings = response.json()
        if holdings:
            holding = holdings[0]
            expected_qty = 150
            # (100*50 + 50*60) / 150 = 8000 / 150 = 53.33
            expected_avg = 53.33
            qty_match = holding['quantity'] == expected_qty
            avg_match = abs(holding['avg_cost'] - expected_avg) < 0.02
            
            print_result(qty_match, f"Holdings quantity: {holding['quantity']} (expected: {expected_qty})")
            print_result(avg_match, f"Average cost: ${holding['avg_cost']:.2f} (expected: ${expected_avg:.2f})")
        
        # Verify cash balance
        response = requests.get(f"{BASE_URL}/accounts/{account_id}")
        account = response.json()
        expected_balance = 10000 - (100 * 50) - (50 * 60)
        balance_match = abs(account['cash_balance'] - expected_balance) < 0.01
        print_result(balance_match, f"Cash balance: ${account['cash_balance']:.2f} (expected: ${expected_balance:.2f})")
    else:
        print_result(False, f"Failed to fill order: {response.text}")
else:
    print_result(False, f"Failed to create order: {response.text}")

# Test 4: SELL order
print_test_header("Test 3: SELL Order")
sell_order = {
    "account_id": account_id,
    "security_id": security_id,
    "side": "SELL",
    "type": "LIMIT",
    "quantity": 50,
    "limit_price": 70.0
}

response = requests.post(f"{BASE_URL}/orders", json=sell_order)
if response.status_code == 201:
    order_id_3 = response.json()['order_id']
    print_result(True, f"Created SELL order for 50 shares at $70")
    
    response = requests.put(f"{BASE_URL}/orders/{order_id_3}/status", json={"status": "FILLED"})
    if response.status_code == 200:
        print_result(True, f"Order filled: {response.json()['details']}")
        
        # Verify holdings - should be 100 shares remaining
        response = requests.get(f"{BASE_URL}/accounts/{account_id}/holdings")
        holdings = response.json()
        if holdings:
            holding = holdings[0]
            expected_qty = 100
            qty_match = holding['quantity'] == expected_qty
            print_result(qty_match, f"Holdings quantity: {holding['quantity']} (expected: {expected_qty})")
        
        # Verify cash balance - should increase by 50 * 70 = $3500
        response = requests.get(f"{BASE_URL}/accounts/{account_id}")
        account = response.json()
        expected_balance = 10000 - (100 * 50) - (50 * 60) + (50 * 70)
        balance_match = abs(account['cash_balance'] - expected_balance) < 0.01
        print_result(balance_match, f"Cash balance: ${account['cash_balance']:.2f} (expected: ${expected_balance:.2f})")
    else:
        print_result(False, f"Failed to fill order: {response.text}")
else:
    print_result(False, f"Failed to create order: {response.text}")

# Test 5: Insufficient funds
print_test_header("Test 4: Error Case - Insufficient Funds")
big_order = {
    "account_id": account_id,
    "security_id": security_id,
    "side": "BUY",
    "type": "LIMIT",
    "quantity": 1000,
    "limit_price": 100.0
}

response = requests.post(f"{BASE_URL}/orders", json=big_order)
if response.status_code == 201:
    order_id_4 = response.json()['order_id']
    print_result(True, f"Created BUY order for 1000 shares at $100 (costs $100,000)")
    
    response = requests.put(f"{BASE_URL}/orders/{order_id_4}/status", json={"status": "FILLED"})
    if response.status_code == 400:
        error_msg = response.json().get('error', '')
        has_insufficient = 'insufficient' in error_msg.lower()
        print_result(has_insufficient, f"Order rejected with error: {error_msg}")
    else:
        print_result(False, f"Order should have been rejected but got: {response.status_code}")
else:
    print_result(False, f"Failed to create order: {response.text}")

# Test 6: Insufficient shares
print_test_header("Test 5: Error Case - Insufficient Shares")
oversell_order = {
    "account_id": account_id,
    "security_id": security_id,
    "side": "SELL",
    "type": "LIMIT",
    "quantity": 200,  # We only have 100
    "limit_price": 50.0
}

response = requests.post(f"{BASE_URL}/orders", json=oversell_order)
if response.status_code == 201:
    order_id_5 = response.json()['order_id']
    print_result(True, f"Created SELL order for 200 shares (only have 100)")
    
    response = requests.put(f"{BASE_URL}/orders/{order_id_5}/status", json={"status": "FILLED"})
    if response.status_code == 400:
        error_msg = response.json().get('error', '')
        has_insufficient = 'insufficient' in error_msg.lower()
        print_result(has_insufficient, f"Order rejected with error: {error_msg}")
    else:
        print_result(False, f"Order should have been rejected but got: {response.status_code}")
else:
    print_result(False, f"Failed to create order: {response.text}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
