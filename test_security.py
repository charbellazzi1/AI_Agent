#!/usr/bin/env python3
"""
Simple test script to verify security features are working.
Run this after deploying the updated backend.
"""

import requests
import time
import json

# Configuration
BASE_URL = "https://restoai-sigma.vercel.app"
# For local testing: BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test that health check works and is not rate limited"""
    print("Testing health check endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        print(f"Health check status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Response: {data}")
            return True
    except Exception as e:
        print(f"Health check failed: {e}")
    return False

def test_rate_limiting():
    """Test rate limiting on chat endpoint"""
    print("\nTesting rate limiting...")
    print("Making multiple requests to trigger rate limit...")
    
    # Make requests quickly to trigger rate limit
    for i in range(35):  # Chat limit is 30 per minute
        try:
            response = requests.post(
                f"{BASE_URL}/api/chat",
                json={"message": f"test message {i}"},
                headers={"User-Agent": "TestClient/1.0"}
            )
            print(f"Request {i+1}: Status {response.status_code}")
            
            if response.status_code == 429:
                print("✓ Rate limiting is working!")
                data = response.json()
                print(f"Rate limit response: {data}")
                return True
                
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
            
        # Small delay to avoid overwhelming the server
        time.sleep(0.1)
    
    print("⚠️ Rate limiting may not be working - no 429 responses received")
    return False

def test_request_validation():
    """Test request validation with suspicious User-Agent"""
    print("\nTesting request validation...")
    
    # Test with suspicious User-Agent
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={"message": "test"},
            headers={"User-Agent": "SuspiciousBot/1.0"}
        )
        
        if response.status_code == 403:
            print("✓ Request validation is working!")
            data = response.json()
            print(f"Validation response: {data}")
            return True
        else:
            print(f"⚠️ Expected 403, got {response.status_code}")
            
    except Exception as e:
        print(f"Request validation test failed: {e}")
    
    return False

def test_security_headers():
    """Test that security headers are present"""
    print("\nTesting security headers...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        headers = response.headers
        
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Referrer-Policy'
        ]
        
        found_headers = []
        for header in expected_headers:
            if header in headers:
                found_headers.append(header)
                print(f"✓ {header}: {headers[header]}")
            else:
                print(f"✗ Missing header: {header}")
        
        if len(found_headers) == len(expected_headers):
            print("✓ All security headers present!")
            return True
        else:
            print(f"⚠️ Only {len(found_headers)}/{len(expected_headers)} headers found")
            
    except Exception as e:
        print(f"Security headers test failed: {e}")
    
    return False

def test_admin_endpoint():
    """Test admin endpoint with and without proper key"""
    print("\nTesting admin endpoint...")
    
    # Test without admin key
    try:
        response = requests.get(f"{BASE_URL}/api/admin/stats")
        if response.status_code == 401:
            print("✓ Admin endpoint properly protected (no key)")
        else:
            print(f"⚠️ Expected 401, got {response.status_code}")
    except Exception as e:
        print(f"Admin endpoint test failed: {e}")
    
    # Test with admin key (if you know it)
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"X-Admin-Key": "admin123"}  # Default key
        )
        if response.status_code == 200:
            print("✓ Admin endpoint works with proper key")
            data = response.json()
            print(f"Admin response: {json.dumps(data, indent=2)}")
            return True
        else:
            print(f"⚠️ Admin endpoint returned {response.status_code}")
    except Exception as e:
        print(f"Admin endpoint with key test failed: {e}")
    
    return False

def main():
    """Run all security tests"""
    print("=== Security Features Test ===")
    print(f"Testing API at: {BASE_URL}")
    print()
    
    tests = [
        ("Health Check", test_health_check),
        ("Security Headers", test_security_headers),
        ("Request Validation", test_request_validation),
        ("Admin Endpoint", test_admin_endpoint),
        ("Rate Limiting", test_rate_limiting),  # Run this last as it may block other requests
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(1)  # Brief pause between tests
    
    print("\n=== Test Results ===")
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nOverall: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 All security features are working correctly!")
    else:
        print("⚠️ Some security features may need attention.")

if __name__ == "__main__":
    main()
