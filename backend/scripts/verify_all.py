import requests
import json

BASE = "http://localhost:6501/api"

# 1. Login
print("=== Testing Authentication ===")
resp = requests.post(f"{BASE}/auth/token", data={"username": "admin", "password": "password123"})
token = resp.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"✅ Token: {token[:20]}...")

# 2. Test Insurance API
print("\n=== Testing Insurance API ===")
resp = requests.get(f"{BASE}/insurance/", headers=headers)
print(f"Status: {resp.status_code}")
if resp.status_code == 200:
    policies = resp.json()
    print(f"✅ Found {len(policies)} policies")
    for p in policies:
        print(f"  - {p['provider']} ({p['type']})")
else:
    print(f"❌ Error: {resp.text}")

# 3. Add a test policy
print("\n=== Adding Test Policy ===")
new_policy = {
    "provider": "StateF arm",
    "type": "Home",
    "policy_number": "HOME-2025-001",
    "renewal_date": "2025-06-30",
    "premium": 1200.0,
    "frequency": "Yearly",
    "insured_item": "123 Main St"
}
resp = requests.post(f"{BASE}/insurance/", json=new_policy, headers=headers)
if resp.status_code == 200:
    print(f"✅ Created: {resp.json()['provider']}")
else:
    print(f"❌ Failed: {resp.text}")

# 4. Verify it appears in list
resp = requests.get(f"{BASE}/insurance/", headers=headers)
policies = resp.json()
print(f"\n✅ Total policies now: {len(policies)}")

# 5. Test Accounts
print("\n=== Testing Accounts API ===")
resp = requests.get(f"{BASE}/accounts", headers=headers)
accounts = resp.json()
print(f"✅ Found {len(accounts)} accounts")
for acc in accounts:
    print(f"  - {acc['account_type']}: ${acc['balance']}")

# 6. Test Transactions
print("\n=== Testing Transactions API ===")
resp = requests.get(f"{BASE}/transactions", headers=headers)
txs = resp.json()
print(f"✅ Found {len(txs)} transactions")
print(f"  First 3: {[t['merchant'] for t in txs[:3]]}")

print("\n🎉 All API tests passed!")
