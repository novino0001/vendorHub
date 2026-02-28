#!/usr/bin/env python3
"""
Comprehensive Backend API Testing - Final Verification
Tests all critical endpoints with proper error handling
"""

import requests
import json
import sys
import uuid

# Configuration
BASE_URL = "https://contractor-hub-125.preview.emergentagent.com/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

def test_comprehensive_backend():
    """Test all backend endpoints comprehensively"""
    session = requests.Session()
    results = []
    
    def log_result(test_name, success, details=""):
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   {details}")
        results.append({"test": test_name, "success": success, "details": details})
    
    print("🚀 COMPREHENSIVE BACKEND API TESTING")
    print("=" * 60)
    
    # 1. Authentication Tests
    print("\n🔐 AUTHENTICATION TESTS")
    
    # Login
    login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
    response = session.post(f"{BASE_URL}/auth/login", json=login_data, timeout=30)
    
    if response.status_code == 200:
        token_data = response.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        log_result("Login with valid credentials", True, f"User ID: {token_data.get('user_id')}")
    else:
        log_result("Login with valid credentials", False, f"Status: {response.status_code}")
        return False
    
    # Invalid login
    invalid_login = {"email": TEST_EMAIL, "password": "wrongpassword"}
    response = session.post(f"{BASE_URL}/auth/login", json=invalid_login, timeout=30)
    log_result("Login with invalid credentials", response.status_code == 401, f"Status: {response.status_code}")
    
    # Get current user
    response = session.get(f"{BASE_URL}/auth/me", headers=headers, timeout=30)
    if response.status_code == 200:
        user_data = response.json()
        log_result("Get current user profile", True, f"Role: {user_data.get('role')}, Email: {user_data.get('email')}")
    else:
        log_result("Get current user profile", False, f"Status: {response.status_code}")
    
    # 2. Vendor Signup Test
    print("\n📝 VENDOR SIGNUP TESTS")
    
    new_vendor_data = {
        "vendor_name": "Test New Contractor Ltd",
        "email": f"newvendor_{uuid.uuid4().hex[:8]}@example.com",
        "phone": "+919876543210",
        "password": "password123",
        "gst_no": "29ABCDE1234F1Z5",
        "revenue": 3000000.0,
        "employee_count": 30,
        "categories": ["civil", "electrical"],
        "service_locations": ["Maharashtra - Mumbai", "Gujarat - Ahmedabad"],
        "short_bio": "New contractor specializing in civil and electrical projects."
    }
    
    response = session.post(f"{BASE_URL}/auth/signup/vendor", json=new_vendor_data, timeout=30)
    log_result("Vendor signup with valid data", response.status_code == 201, f"Status: {response.status_code}")
    
    # Duplicate email test
    response = session.post(f"{BASE_URL}/auth/signup/vendor", json=new_vendor_data, timeout=30)
    log_result("Duplicate email validation", response.status_code == 400, f"Status: {response.status_code}")
    
    # 3. Vendor Profile Tests
    print("\n👥 VENDOR PROFILE TESTS")
    
    # Get my vendor profile (private)
    response = session.get(f"{BASE_URL}/vendors/me", headers=headers, timeout=30)
    if response.status_code == 200:
        private_profile = response.json()
        has_sensitive = all(field in private_profile for field in ["gst_no", "revenue", "employee_count"])
        log_result("Get my vendor profile (private)", has_sensitive, f"Contains sensitive data: {has_sensitive}")
    else:
        log_result("Get my vendor profile (private)", False, f"Status: {response.status_code}")
    
    # Update vendor profile
    update_data = {
        "vendor_name": "Updated Test Contractor Ltd",
        "short_bio": "Updated bio with comprehensive testing and validation.",
        "employee_count": 40
    }
    
    response = session.put(f"{BASE_URL}/vendors/me", json=update_data, headers=headers, timeout=30)
    if response.status_code == 200:
        updated_profile = response.json()
        updated_correctly = (updated_profile.get("vendor_name") == update_data["vendor_name"] and 
                           updated_profile.get("employee_count") == update_data["employee_count"])
        log_result("Update vendor profile", updated_correctly, f"Profile updated: {updated_correctly}")
    else:
        log_result("Update vendor profile", False, f"Status: {response.status_code}")
    
    # 4. Vendors Listing Tests
    print("\n📋 VENDORS LISTING TESTS")
    
    # Basic listing
    response = session.get(f"{BASE_URL}/vendors", headers=headers, timeout=30)
    if response.status_code == 200:
        vendors_data = response.json()
        has_pagination = all(field in vendors_data for field in ["vendors", "total", "page", "per_page", "total_pages"])
        log_result("Vendors list with pagination", has_pagination, f"Total vendors: {vendors_data.get('total')}")
        
        # Get a vendor ID for public profile test
        if vendors_data.get("vendors"):
            vendor_id = vendors_data["vendors"][0]["id"]
            
            # Public vendor profile
            response = session.get(f"{BASE_URL}/vendors/{vendor_id}", headers=headers, timeout=30)
            if response.status_code == 200:
                public_profile = response.json()
                no_sensitive = not any(field in public_profile for field in ["gst_no", "revenue", "employee_count"])
                log_result("Get vendor public profile", no_sensitive, f"No sensitive data exposed: {no_sensitive}")
            else:
                log_result("Get vendor public profile", False, f"Status: {response.status_code}")
    else:
        log_result("Vendors list with pagination", False, f"Status: {response.status_code}")
    
    # Category filter
    response = session.get(f"{BASE_URL}/vendors?category=civil", headers=headers, timeout=30)
    log_result("Vendors category filter", response.status_code == 200, f"Status: {response.status_code}")
    
    # Location search
    response = session.get(f"{BASE_URL}/vendors?location=Mumbai", headers=headers, timeout=30)
    log_result("Vendors location search", response.status_code == 200, f"Status: {response.status_code}")
    
    # Pagination
    response = session.get(f"{BASE_URL}/vendors?page=1&per_page=3", headers=headers, timeout=30)
    if response.status_code == 200:
        paginated_data = response.json()
        correct_pagination = paginated_data.get("per_page") == 3
        log_result("Vendors pagination", correct_pagination, f"Per page: {paginated_data.get('per_page')}")
    else:
        log_result("Vendors pagination", False, f"Status: {response.status_code}")
    
    # 5. Firms Tests
    print("\n🏢 FIRMS TESTS")
    
    # Firms listing
    response = session.get(f"{BASE_URL}/firms", headers=headers, timeout=30)
    if response.status_code == 200:
        firms_data = response.json()
        has_pagination = all(field in firms_data for field in ["firms", "total", "page", "per_page", "total_pages"])
        log_result("Firms list with pagination", has_pagination, f"Total firms: {firms_data.get('total')}")
        
        if firms_data.get("firms"):
            firm_id = firms_data["firms"][0]["id"]
            
            # Individual firm details
            response = session.get(f"{BASE_URL}/firms/{firm_id}", headers=headers, timeout=30)
            if response.status_code == 200:
                firm_details = response.json()
                has_following_status = "is_following" in firm_details
                log_result("Get firm details", has_following_status, f"Firm: {firm_details.get('name')}")
                
                # 6. Follow/Unfollow Flow
                print("\n❤️ FOLLOW/UNFOLLOW TESTS")
                
                # Follow firm
                response = session.post(f"{BASE_URL}/firms/{firm_id}/follow", headers=headers, timeout=30)
                if response.status_code == 200:
                    follow_response = response.json()
                    log_result("Follow firm", follow_response.get("is_following") == True, "Successfully followed")
                    
                    # Get following list
                    response = session.get(f"{BASE_URL}/vendors/me/following", headers=headers, timeout=30)
                    if response.status_code == 200:
                        following_data = response.json()
                        has_followed_firms = "firms" in following_data and following_data.get("total", 0) > 0
                        log_result("Get following list", has_followed_firms, f"Following {following_data.get('total')} firms")
                    else:
                        log_result("Get following list", False, f"Status: {response.status_code}")
                    
                    # Unfollow firm
                    response = session.delete(f"{BASE_URL}/firms/{firm_id}/unfollow", headers=headers, timeout=30)
                    if response.status_code == 200:
                        unfollow_response = response.json()
                        log_result("Unfollow firm", unfollow_response.get("is_following") == False, "Successfully unfollowed")
                    else:
                        log_result("Unfollow firm", False, f"Status: {response.status_code}")
                else:
                    log_result("Follow firm", False, f"Status: {response.status_code}")
            else:
                log_result("Get firm details", False, f"Status: {response.status_code}")
    else:
        log_result("Firms list with pagination", False, f"Status: {response.status_code}")
    
    # 7. Error Handling Tests
    print("\n⚠️ ERROR HANDLING TESTS")
    
    # Invalid firm ID
    response = session.get(f"{BASE_URL}/firms/invalid_id", headers=headers, timeout=30)
    log_result("Invalid firm ID handling", response.status_code == 400, f"Status: {response.status_code}")
    
    # Non-existent firm
    fake_id = "507f1f77bcf86cd799439011"
    response = session.get(f"{BASE_URL}/firms/{fake_id}", headers=headers, timeout=30)
    log_result("Non-existent firm handling", response.status_code == 404, f"Status: {response.status_code}")
    
    # Unauthorized access
    response = session.get(f"{BASE_URL}/auth/me", timeout=30)  # No auth header
    log_result("Unauthorized access protection", response.status_code == 403, f"Status: {response.status_code}")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 FINAL TEST SUMMARY")
    print("=" * 60)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result["success"])
    failed_tests = total_tests - passed_tests
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {failed_tests} ❌")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests > 0:
        print("\n❌ FAILED TESTS:")
        for result in results:
            if not result["success"]:
                print(f"  - {result['test']}: {result['details']}")
    else:
        print("\n🎉 ALL TESTS PASSED! Backend API is fully functional.")
    
    return failed_tests == 0

if __name__ == "__main__":
    print("Contractor Hub - Comprehensive Backend API Testing")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
    print()
    
    success = test_comprehensive_backend()
    sys.exit(0 if success else 1)