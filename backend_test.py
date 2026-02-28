#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Contractor Hub
Tests all API endpoints with various scenarios including authentication, validation, and error handling.
"""

import requests
import json
import sys
from datetime import datetime
import uuid

# Configuration
BASE_URL = "https://contractor-hub-125.preview.emergentagent.com/api"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "password123"

# Test data
VALID_VENDOR_DATA = {
    "vendor_name": "Test Contractor Ltd",
    "email": f"testvendor_{uuid.uuid4().hex[:8]}@example.com",
    "phone": "+919876543210",
    "password": "password123",
    "gst_no": "29ABCDE1234F1Z5",
    "revenue": 2500000.0,
    "employee_count": 25,
    "categories": ["civil", "mechanical"],
    "service_locations": ["Maharashtra - Mumbai", "Karnataka - Bangalore"],
    "short_bio": "Experienced contractor specializing in civil and mechanical projects with 15+ years in the industry."
}

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.auth_token = None
        self.test_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Log test results"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"   Details: {details}")
        if not success and response_data:
            print(f"   Response: {response_data}")
        print()
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "response": response_data
        })
    
    def make_request(self, method, endpoint, data=None, headers=None, auth_required=True):
        """Make HTTP request with proper headers"""
        url = f"{BASE_URL}{endpoint}"
        req_headers = {"Content-Type": "application/json"}
        
        if auth_required and self.auth_token:
            req_headers["Authorization"] = f"Bearer {self.auth_token}"
        
        if headers:
            req_headers.update(headers)
        
        try:
            if method.upper() == "GET":
                response = self.session.get(url, headers=req_headers)
            elif method.upper() == "POST":
                response = self.session.post(url, json=data, headers=req_headers)
            elif method.upper() == "PUT":
                response = self.session.put(url, json=data, headers=req_headers)
            elif method.upper() == "DELETE":
                response = self.session.delete(url, headers=req_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            return response
        except Exception as e:
            print(f"Request failed: {e}")
            return None

    def test_seed_data(self):
        """Test seed data creation"""
        print("🌱 Testing Seed Data Creation...")
        
        response = self.make_request("POST", "/seed-data", auth_required=False)
        if response and response.status_code in [200, 201]:
            data = response.json()
            self.log_test("Seed Data Creation", True, f"Created {data.get('vendors', 0)} vendors and {data.get('firms', 0)} firms")
            return True
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Seed Data Creation", False, f"Status: {response.status_code if response else 'None'}", error_msg)
            return False

    def test_vendor_signup(self):
        """Test vendor signup with various scenarios"""
        print("📝 Testing Vendor Signup...")
        
        # Test valid signup
        response = self.make_request("POST", "/auth/signup/vendor", VALID_VENDOR_DATA, auth_required=False)
        if response and response.status_code == 201:
            data = response.json()
            if "access_token" in data and "user_id" in data:
                self.log_test("Valid Vendor Signup", True, f"User ID: {data['user_id']}")
            else:
                self.log_test("Valid Vendor Signup", False, "Missing token or user_id in response", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Valid Vendor Signup", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        # Test duplicate email
        response = self.make_request("POST", "/auth/signup/vendor", VALID_VENDOR_DATA, auth_required=False)
        if response and response.status_code == 400:
            self.log_test("Duplicate Email Validation", True, "Correctly rejected duplicate email")
        else:
            self.log_test("Duplicate Email Validation", False, f"Expected 400, got {response.status_code if response else 'None'}")
        
        # Test invalid GST format
        invalid_gst_data = VALID_VENDOR_DATA.copy()
        invalid_gst_data["email"] = f"invalid_gst_{uuid.uuid4().hex[:8]}@example.com"
        invalid_gst_data["gst_no"] = "INVALID_GST"
        
        response = self.make_request("POST", "/auth/signup/vendor", invalid_gst_data, auth_required=False)
        if response and response.status_code == 422:
            self.log_test("Invalid GST Validation", True, "Correctly rejected invalid GST format")
        else:
            self.log_test("Invalid GST Validation", False, f"Expected 422, got {response.status_code if response else 'None'}")
        
        # Test invalid phone format
        invalid_phone_data = VALID_VENDOR_DATA.copy()
        invalid_phone_data["email"] = f"invalid_phone_{uuid.uuid4().hex[:8]}@example.com"
        invalid_phone_data["phone"] = "123"
        
        response = self.make_request("POST", "/auth/signup/vendor", invalid_phone_data, auth_required=False)
        if response and response.status_code == 422:
            self.log_test("Invalid Phone Validation", True, "Correctly rejected invalid phone format")
        else:
            self.log_test("Invalid Phone Validation", False, f"Expected 422, got {response.status_code if response else 'None'}")

    def test_login(self):
        """Test login functionality"""
        print("🔐 Testing Login...")
        
        # Test valid login
        login_data = {"email": TEST_EMAIL, "password": TEST_PASSWORD}
        response = self.make_request("POST", "/auth/login", login_data, auth_required=False)
        
        if response and response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                self.auth_token = data["access_token"]
                self.test_user_id = data.get("user_id")
                self.log_test("Valid Login", True, f"Token received, User ID: {self.test_user_id}")
            else:
                self.log_test("Valid Login", False, "No access token in response", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Valid Login", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        # Test invalid credentials
        invalid_login = {"email": TEST_EMAIL, "password": "wrongpassword"}
        response = self.make_request("POST", "/auth/login", invalid_login, auth_required=False)
        
        if response and response.status_code == 401:
            self.log_test("Invalid Credentials", True, "Correctly rejected invalid password")
        else:
            self.log_test("Invalid Credentials", False, f"Expected 401, got {response.status_code if response else 'None'}")

    def test_get_current_user(self):
        """Test getting current user profile"""
        print("👤 Testing Get Current User...")
        
        if not self.auth_token:
            self.log_test("Get Current User", False, "No auth token available")
            return
        
        response = self.make_request("GET", "/auth/me")
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["id", "email", "role"]
            if all(field in data for field in required_fields):
                self.log_test("Get Current User", True, f"Role: {data.get('role')}, Email: {data.get('email')}")
            else:
                self.log_test("Get Current User", False, f"Missing required fields: {required_fields}", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Get Current User", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        # Test without token
        response = self.make_request("GET", "/auth/me", auth_required=False)
        if response and response.status_code == 403:
            self.log_test("Unauthorized Access Protection", True, "Correctly rejected request without token")
        else:
            self.log_test("Unauthorized Access Protection", False, f"Expected 403, got {response.status_code if response else 'None'}")

    def test_vendors_list(self):
        """Test vendors listing with filters and pagination"""
        print("📋 Testing Vendors List...")
        
        if not self.auth_token:
            self.log_test("Vendors List", False, "No auth token available")
            return
        
        # Test basic listing
        response = self.make_request("GET", "/vendors")
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["vendors", "total", "page", "per_page", "total_pages"]
            if all(field in data for field in required_fields):
                self.log_test("Basic Vendors List", True, f"Found {data['total']} vendors, Page {data['page']}/{data['total_pages']}")
            else:
                self.log_test("Basic Vendors List", False, f"Missing pagination fields", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Basic Vendors List", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        # Test category filter
        response = self.make_request("GET", "/vendors?category=civil")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Category Filter", True, f"Civil category filter returned {len(data.get('vendors', []))} vendors")
        else:
            self.log_test("Category Filter", False, f"Status: {response.status_code if response else 'None'}")
        
        # Test location search
        response = self.make_request("GET", "/vendors?location=Mumbai")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Location Search", True, f"Mumbai location search returned {len(data.get('vendors', []))} vendors")
        else:
            self.log_test("Location Search", False, f"Status: {response.status_code if response else 'None'}")
        
        # Test pagination
        response = self.make_request("GET", "/vendors?page=1&per_page=3")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("per_page") == 3:
                self.log_test("Pagination", True, f"Pagination working: {len(data.get('vendors', []))} vendors per page")
            else:
                self.log_test("Pagination", False, "Pagination parameters not respected", data)
        else:
            self.log_test("Pagination", False, f"Status: {response.status_code if response else 'None'}")

    def test_vendor_profiles(self):
        """Test vendor profile endpoints"""
        print("👥 Testing Vendor Profiles...")
        
        if not self.auth_token:
            self.log_test("Vendor Profiles", False, "No auth token available")
            return
        
        # Test get my vendor profile
        response = self.make_request("GET", "/vendors/me")
        if response and response.status_code == 200:
            data = response.json()
            # Should include sensitive fields like GST and revenue
            sensitive_fields = ["gst_no", "revenue", "employee_count"]
            if all(field in data for field in sensitive_fields):
                self.log_test("Get My Vendor Profile", True, f"Private profile with sensitive data: {data.get('vendor_name')}")
            else:
                self.log_test("Get My Vendor Profile", False, f"Missing sensitive fields: {sensitive_fields}", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Get My Vendor Profile", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        # Get a vendor ID for public profile test
        vendors_response = self.make_request("GET", "/vendors?per_page=1")
        if vendors_response and vendors_response.status_code == 200:
            vendors_data = vendors_response.json()
            if vendors_data.get("vendors"):
                vendor_id = vendors_data["vendors"][0]["id"]
                
                # Test public vendor profile
                response = self.make_request("GET", f"/vendors/{vendor_id}")
                if response and response.status_code == 200:
                    data = response.json()
                    # Should NOT include sensitive fields
                    sensitive_fields = ["gst_no", "revenue", "employee_count"]
                    has_sensitive = any(field in data for field in sensitive_fields)
                    if not has_sensitive:
                        self.log_test("Get Public Vendor Profile", True, f"Public profile without sensitive data: {data.get('vendor_name')}")
                    else:
                        self.log_test("Get Public Vendor Profile", False, "Public profile contains sensitive data", data)
                else:
                    self.log_test("Get Public Vendor Profile", False, f"Status: {response.status_code if response else 'None'}")

    def test_vendor_profile_update(self):
        """Test vendor profile update"""
        print("✏️ Testing Vendor Profile Update...")
        
        if not self.auth_token:
            self.log_test("Vendor Profile Update", False, "No auth token available")
            return
        
        # Test profile update
        update_data = {
            "vendor_name": "Updated Test Contractor Ltd",
            "short_bio": "Updated bio with new information about our services and expertise.",
            "employee_count": 30
        }
        
        response = self.make_request("PUT", "/vendors/me", update_data)
        if response and response.status_code == 200:
            data = response.json()
            if data.get("vendor_name") == update_data["vendor_name"] and data.get("employee_count") == update_data["employee_count"]:
                self.log_test("Vendor Profile Update", True, f"Successfully updated profile: {data.get('vendor_name')}")
            else:
                self.log_test("Vendor Profile Update", False, "Update data not reflected in response", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Vendor Profile Update", False, f"Status: {response.status_code if response else 'None'}", error_msg)

    def test_firms_endpoints(self):
        """Test firms-related endpoints"""
        print("🏢 Testing Firms Endpoints...")
        
        if not self.auth_token:
            self.log_test("Firms Endpoints", False, "No auth token available")
            return
        
        # Test firms listing
        response = self.make_request("GET", "/firms")
        if response and response.status_code == 200:
            data = response.json()
            required_fields = ["firms", "total", "page", "per_page", "total_pages"]
            if all(field in data for field in required_fields) and data.get("firms"):
                firm_id = data["firms"][0]["id"]
                self.log_test("Firms List", True, f"Found {data['total']} firms")
                
                # Test individual firm details
                firm_response = self.make_request("GET", f"/firms/{firm_id}")
                if firm_response and firm_response.status_code == 200:
                    firm_data = firm_response.json()
                    if "is_following" in firm_data:
                        self.log_test("Get Firm Details", True, f"Firm: {firm_data.get('name')}, Following: {firm_data.get('is_following')}")
                        return firm_id  # Return for follow/unfollow tests
                    else:
                        self.log_test("Get Firm Details", False, "Missing is_following field", firm_data)
                else:
                    self.log_test("Get Firm Details", False, f"Status: {firm_response.status_code if firm_response else 'None'}")
            else:
                self.log_test("Firms List", False, "Missing required fields or no firms", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Firms List", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        return None

    def test_follow_unfollow_flow(self, firm_id):
        """Test complete follow/unfollow flow"""
        print("❤️ Testing Follow/Unfollow Flow...")
        
        if not self.auth_token or not firm_id:
            self.log_test("Follow/Unfollow Flow", False, "No auth token or firm ID available")
            return
        
        # Test follow firm
        response = self.make_request("POST", f"/firms/{firm_id}/follow")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("is_following") == True:
                self.log_test("Follow Firm", True, f"Successfully followed firm: {data.get('message')}")
            else:
                self.log_test("Follow Firm", False, "Follow response incorrect", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Follow Firm", False, f"Status: {response.status_code if response else 'None'}", error_msg)
            return
        
        # Test follow again (should handle duplicate)
        response = self.make_request("POST", f"/firms/{firm_id}/follow")
        if response and response.status_code == 200:
            data = response.json()
            self.log_test("Duplicate Follow Handling", True, f"Handled duplicate follow: {data.get('message')}")
        else:
            self.log_test("Duplicate Follow Handling", False, f"Status: {response.status_code if response else 'None'}")
        
        # Test get following list
        response = self.make_request("GET", "/vendors/me/following")
        if response and response.status_code == 200:
            data = response.json()
            if "firms" in data and data.get("total", 0) > 0:
                self.log_test("Get Following List", True, f"Following {data['total']} firms")
            else:
                self.log_test("Get Following List", False, "No firms in following list", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Get Following List", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        # Test unfollow firm
        response = self.make_request("DELETE", f"/firms/{firm_id}/unfollow")
        if response and response.status_code == 200:
            data = response.json()
            if data.get("is_following") == False:
                self.log_test("Unfollow Firm", True, f"Successfully unfollowed firm: {data.get('message')}")
            else:
                self.log_test("Unfollow Firm", False, "Unfollow response incorrect", data)
        else:
            error_msg = response.json() if response else "No response"
            self.log_test("Unfollow Firm", False, f"Status: {response.status_code if response else 'None'}", error_msg)
        
        # Test unfollow again (should return 404)
        response = self.make_request("DELETE", f"/firms/{firm_id}/unfollow")
        if response and response.status_code == 404:
            self.log_test("Unfollow Non-followed Firm", True, "Correctly returned 404 for non-followed firm")
        else:
            self.log_test("Unfollow Non-followed Firm", False, f"Expected 404, got {response.status_code if response else 'None'}")

    def test_error_scenarios(self):
        """Test various error scenarios"""
        print("⚠️ Testing Error Scenarios...")
        
        # Test invalid firm ID
        response = self.make_request("GET", "/firms/invalid_id")
        if response and response.status_code == 400:
            self.log_test("Invalid Firm ID", True, "Correctly rejected invalid firm ID")
        else:
            self.log_test("Invalid Firm ID", False, f"Expected 400, got {response.status_code if response else 'None'}")
        
        # Test non-existent firm
        fake_id = "507f1f77bcf86cd799439011"  # Valid ObjectId format but non-existent
        response = self.make_request("GET", f"/firms/{fake_id}")
        if response and response.status_code == 404:
            self.log_test("Non-existent Firm", True, "Correctly returned 404 for non-existent firm")
        else:
            self.log_test("Non-existent Firm", False, f"Expected 404, got {response.status_code if response else 'None'}")

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("🚀 Starting Comprehensive Backend API Testing")
        print("=" * 60)
        
        # Seed data first
        self.test_seed_data()
        
        # Authentication tests
        self.test_vendor_signup()
        self.test_login()
        self.test_get_current_user()
        
        # Vendor tests
        self.test_vendors_list()
        self.test_vendor_profiles()
        self.test_vendor_profile_update()
        
        # Firms tests
        firm_id = self.test_firms_endpoints()
        if firm_id:
            self.test_follow_unfollow_flow(firm_id)
        
        # Error scenarios
        self.test_error_scenarios()
        
        # Summary
        print("=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ FAILED TESTS:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test']}: {result['details']}")
        
        return failed_tests == 0

if __name__ == "__main__":
    print("Contractor Hub - Backend API Testing")
    print(f"Base URL: {BASE_URL}")
    print(f"Test Credentials: {TEST_EMAIL} / {TEST_PASSWORD}")
    print()
    
    tester = APITester()
    success = tester.run_all_tests()
    
    sys.exit(0 if success else 1)