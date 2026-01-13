import requests
import json

BASE_URL = "http://localhost:6501/api"

def test_insurance_flow():
    print("🚀 Starting Insurance API Test...")
    
    # 1. Login to get token (using default admin)
    print("🔑 Authenticating...")
    resp = requests.post(f"{BASE_URL}/auth/token", data={"username": "admin", "password": "password123"})
    if resp.status_code != 200:
        print(f"❌ Login failed: {resp.text}")
        return
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("✅ Authenticated.")

    # 2. Setup New Policy Data
    new_policy = {
        "provider": "TestAuto",
        "type": "Auto",
        "policy_number": "API-TEST-001",
        "renewal_date": "2025-12-31",
        "premium": 150.0,
        "frequency": "Monthly",
        "insured_item": "CyberTruck"
    }

    # 3. Create Policy
    print(f"➕ Creating Policy: {new_policy['provider']}...")
    resp = requests.post(f"{BASE_URL}/insurance/", json=new_policy, headers=headers)
    if resp.status_code == 200:
        print("✅ Policy Created Successfully!")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"❌ Create failed: {resp.text}")
        return

    # 4. List Policies
    print("📋 Listing Policies...")
    resp = requests.get(f"{BASE_URL}/insurance/", headers=headers)
    if resp.status_code == 200:
        policies = resp.json()
        print(f"✅ Found {len(policies)} policies.")
        found = False
        for p in policies:
            if p["policy_number"] == "API-TEST-001":
                found = True
                print("✅ Verified: Created policy exists in list!")
                break
        if not found:
            print("❌ Created policy NOT found in list.")
    else:
        print(f"❌ List failed: {resp.text}")

if __name__ == "__main__":
    test_insurance_flow()
