#!/usr/bin/env python3
"""
Comprehensive Feature Test for Stock Exchange App
Tests all major features as a regular user (Rohit)
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5001/api"
TEST_USER_EMAIL = "rohit@example.com"
TEST_USER_PASSWORD = "demo123"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}{Colors.END}")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.YELLOW}ℹ {msg}{Colors.END}")

# Global token storage
auth_token = None
test_data = {
    'account_id': None,
    'security_id': None,
    'order_id': None,
    'watchlist_id': None
}

def test_login():
    """Test 1: Login as regular user"""
    print_test("1. User Login")
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": TEST_USER_EMAIL,
            "password": TEST_USER_PASSWORD
        })
        
        if response.status_code == 200:
            data = response.json()
            global auth_token
            auth_token = data['token']
            print_success(f"Logged in as {data['user']['full_name']}")
            print_info(f"Role: {data['user']['role']}")
            return True
        else:
            print_error(f"Login failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Login error: {str(e)}")
        return False

def test_get_accounts():
    """Test 2: Get user's accounts"""
    print_test("2. Get User Accounts")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/accounts", headers=headers)
        
        if response.status_code == 200:
            accounts = response.json()
            print_success(f"Retrieved {len(accounts)} accounts")
            for acc in accounts[:3]:  # Show first 3
                print_info(f"  - {acc['name']}: ${acc['cash_balance']}")
            
            # Save first account for order test
            if accounts:
                test_data['account_id'] = accounts[0]['account_id']
            return True
        else:
            print_error(f"Failed to get accounts: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_securities():
    """Test 3: Get available securities"""
    print_test("3. Get Securities")
    
    try:
        response = requests.get(f"{BASE_URL}/securities")
        
        if response.status_code == 200:
            securities = response.json()
            print_success(f"Retrieved {len(securities)} securities")
            for sec in securities[:5]:  # Show first 5
                print_info(f"  - {sec['ticker']}: {sec['name']}")
            
            # Save AAPL for order test
            aapl = next((s for s in securities if s['ticker'] == 'AAPL'), None)
            if aapl:
                test_data['security_id'] = aapl['security_id']
                print_info(f"Using AAPL (security_id: {aapl['security_id'][:8]}...)")
            return True
        else:
            print_error(f"Failed to get securities: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_create_order():
    """Test 4: Create a BUY order"""
    print_test("4. Create BUY Order")
    
    if not test_data['account_id'] or not test_data['security_id']:
        print_error("Missing account_id or security_id")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        order_data = {
            "account_id": test_data['account_id'],
            "security_id": test_data['security_id'],
            "side": "BUY",
            "type": "LIMIT",
            "quantity": 5,
            "limit_price": 150.00
        }
        
        response = requests.post(f"{BASE_URL}/orders", json=order_data, headers=headers)
        
        if response.status_code == 201:
            data = response.json()
            test_data['order_id'] = data['order_id']
            print_success(f"Created BUY order for 5 shares of AAPL at $150")
            print_info(f"Order ID: {data['order_id'][:8]}...")
            return True
        else:
            print_error(f"Failed to create order: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_holdings_before():
    """Test 5a: Get holdings before order fulfillment"""
    print_test("5a. Get Holdings (Before Fill)")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/holdings", headers=headers)
        
        if response.status_code == 200:
            holdings = response.json()
            print_success(f"Current holdings: {len(holdings)}")
            
            aapl_holding = next((h for h in holdings if h['ticker'] == 'AAPL'), None)
            if aapl_holding:
                print_info(f"  AAPL: {aapl_holding['quantity']} shares @ ${aapl_holding['avg_cost']}")
            else:
                print_info("  No AAPL holdings yet")
            return True
        else:
            print_error(f"Failed to get holdings: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_fill_order():
    """Test 5b: Fill the order (test order fulfillment system)"""
    print_test("5b. Fill Order (Test Fulfillment)")
    
    if not test_data['order_id']:
        print_error("No order_id available")
        return False
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.put(
            f"{BASE_URL}/orders/{test_data['order_id']}/status",
            json={"status": "FILLED"},
            headers=headers
        )
        
        if response.status_code == 200:
            print_success("Order marked as FILLED")
            print_info("Order fulfillment system should have updated holdings...")
            return True
        else:
            print_error(f"Failed to fill order: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_holdings_after():
    """Test 5c: Verify holdings were updated"""
    print_test("5c. Verify Holdings Updated")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/holdings", headers=headers)
        
        if response.status_code == 200:
            holdings = response.json()
            print_success(f"Retrieved {len(holdings)} holdings")
            
            aapl_holding = next((h for h in holdings if h['ticker'] == 'AAPL'), None)
            if aapl_holding:
                print_success(f"AAPL holding found!")
                print_info(f"  Quantity: {aapl_holding['quantity']} shares")
                print_info(f"  Avg Cost: ${aapl_holding['avg_cost']:.2f}")
                print_info(f"  Total Value: ${aapl_holding['total_cost']:.2f}")
                
                if aapl_holding['quantity'] >= 5:
                    print_success("✓ Order fulfillment WORKED - shares added!")
                    return True
                else:
                    print_error("Shares not added correctly")
                    return False
            else:
                print_error("AAPL holding not found after fill")
                return False
        else:
            print_error(f"Failed to get holdings: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_create_watchlist():
    """Test 6: Create a watchlist"""
    print_test("6. Create Watchlist")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.post(
            f"{BASE_URL}/watchlists",
            json={"name": f"Test Watchlist {datetime.now().strftime('%H:%M:%S')}"},
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            test_data['watchlist_id'] = data['watchlist_id']
            print_success("Watchlist created successfully!")
            print_info(f"Watchlist ID: {data['watchlist_id'][:8]}...")
            return True
        else:
            print_error(f"Failed to create watchlist: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_get_watchlists():
    """Test 7: Get user's watchlists"""
    print_test("7. Get Watchlists")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/watchlists", headers=headers)
        
        if response.status_code == 200:
            watchlists = response.json()
            print_success(f"Retrieved {len(watchlists)} watchlists")
            for wl in watchlists:
                print_info(f"  - {wl['name']} ({wl['item_count']} items)")
            return True
        else:
            print_error(f"Failed to get watchlists: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_analytics():
    """Test 8: Get analytics data"""
    print_test("8. Analytics - Portfolio Value")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/analytics/portfolio-value", headers=headers)
        
        if response.status_code == 200:
            portfolios = response.json()
            print_success(f"Retrieved portfolio data for {len(portfolios)} accounts")
            for p in portfolios:
                print_info(f"  {p['name']}:")
                print_info(f"    Cash: ${p['cash_balance']:.2f}")
                print_info(f"    Holdings: ${p['holdings_value']:.2f}")
                print_info(f"    Total: ${p['total_value']:.2f}")
            return True
        else:
            print_error(f"Failed to get analytics: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def test_top_holdings():
    """Test 9: Get top holdings"""
    print_test("9. Analytics - Top Holdings")
    
    try:
        headers = {"Authorization": f"Bearer {auth_token}"}
        response = requests.get(f"{BASE_URL}/analytics/top-holdings", headers=headers)
        
        if response.status_code == 200:
            holdings = response.json()
            print_success(f"Top {len(holdings)} holdings:")
            for i, h in enumerate(holdings[:5], 1):
                print_info(f"  {i}. {h['ticker']} - ${h['total_value']:.2f} ({h['total_shares']} shares)")
            return True
        else:
            print_error(f"Failed to get top holdings: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests in sequence"""
    print(f"\n{Colors.BLUE}{'='*60}")
    print(f"STOCK EXCHANGE APP - COMPREHENSIVE FEATURE TEST")
    print(f"Testing as: {TEST_USER_EMAIL}")
    print(f"{'='*60}{Colors.END}\n")
    
    results = []
    
    # Run tests
    results.append(("Login", test_login()))
    if not results[-1][1]:
        print_error("\n❌ LOGIN FAILED - Cannot continue tests")
        return
    
    results.append(("Get Accounts", test_get_accounts()))
    results.append(("Get Securities", test_get_securities()))
    results.append(("Create Order", test_create_order()))
    results.append(("Get Holdings (Before)", test_get_holdings_before()))
    results.append(("Fill Order", test_fill_order()))
    results.append(("Verify Holdings (After)", test_get_holdings_after()))
    results.append(("Create Watchlist", test_create_watchlist()))
    results.append(("Get Watchlists", test_get_watchlists()))
    results.append(("Analytics - Portfolio", test_analytics()))
    results.append(("Analytics - Top Holdings", test_top_holdings()))
    
    # Print summary
    print(f"\n{Colors.BLUE}{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.END}" if result else f"{Colors.RED}FAIL{Colors.END}"
        print(f"  {test_name:<30} {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}")
    if passed == total:
        print(f"{Colors.GREEN}✓ ALL TESTS PASSED ({passed}/{total}){Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠ {passed}/{total} tests passed{Colors.END}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    run_all_tests()
