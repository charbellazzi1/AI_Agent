#!/usr/bin/env python3
"""
Enhanced security test script to verify new features added.
"""

import requests
import time
import json

# Configuration - Updated to current production URL
BASE_URL = "https://restoai-ovkk14wn7-charbels-projects-87309710.vercel.app"

def test_enhanced_security_headers():
    """Test for Content-Security-Policy and other enhanced headers"""
    print("Testing enhanced security headers...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        headers = response.headers
        
        print(f"All headers: {dict(headers)}")
        
        # Check for CSP header specifically
        if 'Content-Security-Policy' in headers:
            print(f"✓ Content-Security-Policy: {headers['Content-Security-Policy']}")
            return True
        else:
            print("⚠️ Content-Security-Policy header not found")
            return False
            
    except Exception as e:
        print(f"Enhanced headers test failed: {e}")
    
    return False

def test_enhanced_admin_endpoint():
    """Test enhanced admin endpoint with new fields"""
    print("\nTesting enhanced admin endpoint...")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers={"X-Admin-Key": "admin123"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"Admin response: {json.dumps(data, indent=2)}")
            
            # Check for new fields
            expected_fields = ['timestamp', 'security_features']
            found_fields = []
            
            for field in expected_fields:
                if field in data:
                    found_fields.append(field)
                    print(f"✓ New field '{field}' present")
                else:
                    print(f"⚠️ New field '{field}' missing")
            
            return len(found_fields) == len(expected_fields)
        else:
            print(f"Admin endpoint returned status: {response.status_code}")
            
    except Exception as e:
        print(f"Enhanced admin test failed: {e}")
    
    return False

def test_enhanced_rate_limit_headers():
    """Test enhanced rate limit response headers"""
    print("\nTesting enhanced rate limit headers...")
    
    # First, trigger rate limit by making many requests
    print("Triggering rate limit...")
    rate_limit_response = None
    
    for i in range(15):
        try:
            response = requests.get(
                f"{BASE_URL}/api/restaurants/cuisines",
                headers={"User-Agent": "TestClient/1.0"}
            )
            
            if response.status_code == 429:
                rate_limit_response = response
                print(f"✓ Rate limit triggered on request {i+1}")
                break
                
        except Exception as e:
            print(f"Request {i+1} failed: {e}")
        
        time.sleep(0.2)
    
    if rate_limit_response:
        headers = rate_limit_response.headers
        print(f"Rate limit headers: {dict(headers)}")
        
        # Check for enhanced headers
        enhanced_headers = ['Retry-After', 'X-RateLimit-Limit', 'X-RateLimit-Remaining']
        found_headers = []
        
        for header in enhanced_headers:
            if header in headers:
                found_headers.append(header)
                print(f"✓ Enhanced header '{header}': {headers[header]}")
            else:
                print(f"⚠️ Enhanced header '{header}' missing")
        
        return len(found_headers) > 0  # At least some enhanced headers should be present
    else:
        print("⚠️ Could not trigger rate limit to test headers")
        return False

def main():
    """Run enhanced security tests"""
    print("=== Enhanced Security Features Test ===")
    print(f"Testing API at: {BASE_URL}")
    print()
    
    tests = [
        ("Enhanced Security Headers (CSP)", test_enhanced_security_headers),
        ("Enhanced Admin Endpoint", test_enhanced_admin_endpoint), 
        ("Enhanced Rate Limit Headers", test_enhanced_rate_limit_headers),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
        
        time.sleep(2)  # Pause between tests
    
    print("\n=== Enhanced Test Results ===")
    for test_name, passed in results:
        status = "✓ PASS" if passed else "⚠️ PENDING/FAIL"
        print(f"{test_name}: {status}")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    print(f"\nOverall: {passed_count}/{total_count} enhanced tests passed")
    
    if passed_count == total_count:
        print("🎉 All enhanced security features are working!")
    elif passed_count > 0:
        print("⚠️ Some enhanced features may still be deploying...")
    else:
        print("❌ Enhanced features not yet deployed or working.")

if __name__ == "__main__":
    main()
