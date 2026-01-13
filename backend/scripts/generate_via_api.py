"""
Generate mock data via API calls
This script uses the running backend API to inject data
"""
import requests
import random
from datetime import date, timedelta
import json

API_BASE = "http://localhost:6501"

# Login to get token
print("Logging in...")
login_response = requests.post(
    f"{API_BASE}/api/auth/token",
    data={"username": "admin", "password": "password123"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.text}")
    exit(1)

token = login_response.json()["access_token"]
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print(f"Logged in successfully! Token: {token[:20]}...")

# Check existing transactions
print("\nChecking existing transactions...")
tx_response = requests.get(f"{API_BASE}/api/transactions", headers=headers)
existing_count = len(tx_response.json())
print(f"Current transactions: {existing_count}")

if existing_count >= 50:
    print("Already have enough transactions. Skipping generation.")
    exit(0)

# Canadian merchants
merchants = [
    ("Costco Wholesale", "Groceries"),
    ("Real Canadian Superstore", "Groceries"),
    ("Tim Hortons", "Dining"),
    ("McDonald's", "Dining"),
    ("Shell Station", "Transport"),
    ("Petro-Canada", "Transport"),
    ("Home Depot", "House"),
    ("Shoppers Drug Mart", "Health"),
    ("Amazon.ca", "Shopping"),
]

print(f"\nGenerating {100 - existing_count} transactions...")

today = date.today()
success_count = 0
error_count = 0

for i in range(100 - existing_count):
    tx_date = today - timedelta(days=i)
    merchant, category = random.choice(merchants)
    amount = -round(random.uniform(10, 300), 2)
    
    transaction = {
        "date": tx_date.isoformat(),
        "merchant": merchant,
        "amount": amount,
        "category": category,
        "status": "Posted" if i > 5 else "draft"
    }
    
    try:
        response = requests.post(
            f"{API_BASE}/api/transactions",
            headers=headers,
            json=transaction
        )
        
        if response.status_code == 200:
            success_count += 1
            if success_count % 10 == 0:
                print(f"  Created {success_count} transactions...")
        else:
            error_count += 1
            if error_count < 5:
                print(f"  Error: {response.status_code} - {response.text[:100]}")
    except Exception as e:
        error_count += 1
        if error_count < 5:
            print(f"  Exception: {e}")

print(f"\nCompleted!")
print(f"  Success: {success_count}")
print(f"  Errors: {error_count}")
print(f"  Total transactions now: {existing_count + success_count}")
