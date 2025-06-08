#!/usr/bin/env python3
"""
API Endpoints Test Script
Tests all API endpoints to ensure they work correctly and prevent 404 errors.
"""

import requests
import json
import sys
from datetime import datetime

# Base URL for testing
BASE_URL = "http://127.0.0.1:8000"

# Color codes for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def test_endpoint(url, method='GET', data=None, expected_status=200):
    """Test a single API endpoint"""
    full_url = f"{BASE_URL}{url}"
    
    try:
        if method == 'GET':
            response = requests.get(full_url, timeout=5)
        elif method == 'POST':
            response = requests.post(full_url, json=data, timeout=5)
        elif method == 'PUT':
            response = requests.put(full_url, json=data, timeout=5)
        
        status_ok = response.status_code == expected_status
        color = Colors.GREEN if status_ok else Colors.RED
        status_text = "✅ PASS" if status_ok else "❌ FAIL"
        
        print(f"{color}{status_text}{Colors.ENDC} {method} {url} → {response.status_code}")
        
        if not status_ok:
            print(f"  Expected: {expected_status}, Got: {response.status_code}")
            if response.status_code == 404:
                print(f"  {Colors.RED}URL not found - check URL patterns{Colors.ENDC}")
            elif response.status_code >= 500:
                print(f"  {Colors.RED}Server error: {response.text[:100]}{Colors.ENDC}")
        
        # Try to parse JSON response
        try:
            response_data = response.json()
            if status_ok and 'error' not in response_data:
                print(f"  {Colors.BLUE}Response keys: {list(response_data.keys())}{Colors.ENDC}")
        except:
            if status_ok:
                print(f"  {Colors.YELLOW}Non-JSON response{Colors.ENDC}")
        
        return status_ok
        
    except requests.exceptions.RequestException as e:
        print(f"{Colors.RED}❌ ERROR{Colors.ENDC} {method} {url} → {str(e)}")
        return False

def main():
    """Test all API endpoints"""
    print(f"{Colors.BOLD}🔍 Testing All API Endpoints{Colors.ENDC}")
    print(f"Base URL: {BASE_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test results
    total_tests = 0
    passed_tests = 0
    
    # Health check endpoints
    print(f"\n{Colors.BOLD}📊 Health & Basic Endpoints{Colors.ENDC}")
    endpoints = [
        ('/', 'GET', None, 200),
        ('/health/', 'GET', None, 200),
    ]
    
    for url, method, data, expected in endpoints:
        total_tests += 1
        if test_endpoint(url, method, data, expected):
            passed_tests += 1
    
    # Dashboard API endpoints
    print(f"\n{Colors.BOLD}📈 Dashboard API Endpoints{Colors.ENDC}")
    endpoints = [
        ('/api/monthly-totals/', 'GET', None, 200),
        ('/api/today-summary/', 'GET', None, 200),
        ('/api/calendar-data/', 'GET', None, 200),
    ]
    
    for url, method, data, expected in endpoints:
        total_tests += 1
        if test_endpoint(url, method, data, expected):
            passed_tests += 1
    
    # Transaction API endpoints
    print(f"\n{Colors.BOLD}💰 Transaction API Endpoints{Colors.ENDC}")
    endpoints = [
        ('/api/transactions/', 'GET', None, 200),
        ('/api/transactions/statistics/', 'GET', None, 200),
    ]
    
    for url, method, data, expected in endpoints:
        total_tests += 1
        if test_endpoint(url, method, data, expected):
            passed_tests += 1
    
    # AI Chat API endpoints
    print(f"\n{Colors.BOLD}🤖 AI Chat API Endpoints{Colors.ENDC}")
    endpoints = [
        ('/api/ai_chat/monthly-totals/', 'GET', None, 200),
        ('/api/ai_chat/meme/weekly/', 'GET', None, 200),
        # Aliases
        ('/api/meme/weekly/', 'GET', None, 200),
        ('/api/chat/confirm/', 'POST', {'confirmed': True}, 200),
    ]
    
    for url, method, data, expected in endpoints:
        total_tests += 1
        if test_endpoint(url, method, data, expected):
            passed_tests += 1
    
    # Future projection endpoints
    print(f"\n{Colors.BOLD}🔮 Future Projection Endpoints{Colors.ENDC}")
    endpoints = [
        ('/api/future-projection/?months=12', 'GET', None, 200),
        ('/api/monthly-analysis/?year=2025&month=6', 'GET', None, 200),
    ]
    
    for url, method, data, expected in endpoints:
        total_tests += 1
        if test_endpoint(url, method, data, expected):
            passed_tests += 1
    
    # Summary
    print("\n" + "=" * 60)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
    color = Colors.GREEN if success_rate >= 90 else Colors.YELLOW if success_rate >= 70 else Colors.RED
    
    print(f"{Colors.BOLD}📊 Test Results Summary{Colors.ENDC}")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {Colors.GREEN}{passed_tests}{Colors.ENDC}")
    print(f"Failed: {Colors.RED}{total_tests - passed_tests}{Colors.ENDC}")
    print(f"Success Rate: {color}{success_rate:.1f}%{Colors.ENDC}")
    
    if success_rate < 100:
        print(f"\n{Colors.YELLOW}⚠️  Some endpoints failed. Check URL patterns and view functions.{Colors.ENDC}")
        return 1
    else:
        print(f"\n{Colors.GREEN}✅ All endpoints working correctly!{Colors.ENDC}")
        return 0

if __name__ == "__main__":
    sys.exit(main()) 