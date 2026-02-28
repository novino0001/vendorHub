#!/usr/bin/env python3
"""
Focused Backend API Testing for specific endpoints that need retesting
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://contractor-hub-125.preview.emergentagent.com/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

def test_key_endpoints():
    """Test the key endpoints that need retesting"""
    session = requests.Session()
    
    print("🔐 Testing Login...")
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = session.post(f"{BASE_URL}/auth/login", json=login_data, timeout=30)
    
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return False
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    
    print("✅ Login successful")
    
    # Test vendor profile update
    print("\n✏️ Testing Vendor Profile Update...")
    update_data = {
        "vendor_name": "Updated Test Contractor Ltd",
        "short_bio": "Updated bio with comprehensive testing information.",
        "employee_count": 35
    }
    
    response = session.put(f"{BASE_URL}/vendors/me", json=update_data, headers=headers, timeout=30)
    if response.status_code == 200:
        data = response.json()
        if data.get("vendor_name") == update_data["vendor_name"]:
            print("✅ Vendor Profile Update - WORKING")
        else:
            print("❌ Vendor Profile Update - Data not updated correctly")
            return False
    else:
        print(f"❌ Vendor Profile Update failed: {response.status_code}")
        return False
    
    # Test firms listing and get a firm ID
    print("\n🏢 Testing Firms List...")
    response = session.get(f"{BASE_URL}/firms", headers=headers, timeout=30)
    if response.status_code == 200:
        firms_data = response.json()
        if firms_data.get("firms"):
            firm_id = firms_data["firms"][0]["id"]
            print("✅ Firms List - WORKING")
            
            # Test follow/unfollow flow
            print("\n❤️ Testing Follow/Unfollow Flow...")
            
            # Follow firm
            response = session.post(f"{BASE_URL}/firms/{firm_id}/follow", headers=headers, timeout=30)
            if response.status_code == 200:
                follow_data = response.json()
                if follow_data.get("is_following") == True:
                    print("✅ Follow Firm - WORKING")
                else:
                    print("❌ Follow Firm - Incorrect response")
                    return False
            else:
                print(f"❌ Follow Firm failed: {response.status_code}")
                return False
            
            # Test get following list
            response = session.get(f"{BASE_URL}/vendors/me/following", headers=headers, timeout=30)
            if response.status_code == 200:
                following_data = response.json()
                if "firms" in following_data and following_data.get("total", 0) > 0:
                    print("✅ Get Following List - WORKING")
                else:
                    print("❌ Get Following List - No firms found")
                    return False
            else:
                print(f"❌ Get Following List failed: {response.status_code}")
                return False
            
            # Unfollow firm
            response = session.delete(f"{BASE_URL}/firms/{firm_id}/unfollow", headers=headers, timeout=30)
            if response.status_code == 200:
                unfollow_data = response.json()
                if unfollow_data.get("is_following") == False:
                    print("✅ Unfollow Firm - WORKING")
                else:
                    print("❌ Unfollow Firm - Incorrect response")
                    return False
            else:
                print(f"❌ Unfollow Firm failed: {response.status_code}")
                return False
            
        else:
            print("❌ Firms List - No firms found")
            return False
    else:
        print(f"❌ Firms List failed: {response.status_code}")
        return False
    
    print("\n🎉 All key endpoints are WORKING correctly!")
    return True

if __name__ == "__main__":
    print("Contractor Hub - Focused Backend API Testing")
    print(f"Base URL: {BASE_URL}")
    print("Testing endpoints that need retesting...\n")
    
    success = test_key_endpoints()
    sys.exit(0 if success else 1)