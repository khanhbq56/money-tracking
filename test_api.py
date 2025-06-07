#!/usr/bin/env python
"""
Simple test script to validate Phase 2 API endpoints.
Run this after starting the Django development server.
"""

import os
import sys
import django
import requests
import json
from datetime import date

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings.development')
django.setup()

# Test configuration
BASE_URL = 'http://127.0.0.1:8000/api'


def test_endpoint(method, url, data=None, expected_status=200):
    """Test an API endpoint and return the response"""
    try:
        if method.upper() == 'GET':
            response = requests.get(url)
        elif method.upper() == 'POST':
            response = requests.post(url, json=data, headers={'Content-Type': 'application/json'})
        elif method.upper() == 'PUT':
            response = requests.put(url, json=data, headers={'Content-Type': 'application/json'})
        
        print(f"\n{method.upper()} {url}")
        print(f"Status: {response.status_code} (expected: {expected_status})")
        
        if response.status_code == expected_status:
            print("✅ PASS")
            try:
                return response.json()
            except:
                return response.text
        else:
            print(f"❌ FAIL - Expected {expected_status}, got {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print(f"❌ CONNECTION ERROR - Make sure Django server is running at {BASE_URL}")
        return None
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None


def main():
    """Run API tests"""
    print("🚀 Testing Phase 2 API Endpoints")
    print("=" * 50)
    
    # Test 1: Get monthly totals
    print("\n📊 Testing Monthly Totals")
    monthly_totals = test_endpoint('GET', f'{BASE_URL}/monthly-totals/')
    
    # Test 2: Get calendar data
    print("\n📅 Testing Calendar Data")
    current_date = date.today()
    calendar_data = test_endpoint('GET', f'{BASE_URL}/calendar-data/?month={current_date.month}&year={current_date.year}')
    
    # Test 3: Get today's summary
    print("\n📝 Testing Today Summary")
    today_summary = test_endpoint('GET', f'{BASE_URL}/today-summary/')
    
    # Test 4: Chat message processing
    print("\n🤖 Testing Chat Processing")
    chat_data = {
        'message': 'coffee 25k',
        'has_voice': False,
        'language': 'vi'
    }
    chat_response = test_endpoint('POST', f'{BASE_URL}/chat/process/', chat_data, 201)
    
    # Test 5: Get translations
    print("\n🌐 Testing Translations")
    translations_vi = test_endpoint('GET', f'{BASE_URL}/translations/vi/')
    translations_en = test_endpoint('GET', f'{BASE_URL}/translations/en/')
    
    # Test 6: Transaction CRUD
    print("\n💰 Testing Transaction CRUD")
    
    # Create a transaction
    transaction_data = {
        'transaction_type': 'expense',
        'amount': 25000,
        'description': 'Test Coffee',
        'date': str(current_date),
        'expense_category': 'coffee'
    }
    created_transaction = test_endpoint('POST', f'{BASE_URL}/transactions/', transaction_data, 201)
    
    # List transactions
    transactions = test_endpoint('GET', f'{BASE_URL}/transactions/')
    
    # Test statistics
    print("\n📈 Testing Statistics")
    stats = test_endpoint('GET', f'{BASE_URL}/transactions/statistics/')
    
    print("\n" + "=" * 50)
    print("🎉 Phase 2 API Testing Complete!")
    
    # Cleanup: Delete the test transaction if it was created
    if created_transaction and 'id' in created_transaction:
        test_endpoint('DELETE', f'{BASE_URL}/transactions/{created_transaction["id"]}/', expected_status=204)
        print("🧹 Cleaned up test transaction")


if __name__ == '__main__':
    main() 