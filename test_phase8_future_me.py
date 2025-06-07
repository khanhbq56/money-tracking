#!/usr/bin/env python
"""
Test script for Phase 8: Future Me Simulator
Tests the API endpoints and calculator functionality
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, date, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'expense_tracker.settings.development')
django.setup()

# Now we can import Django models
from transactions.models import Transaction
from transactions.future_calculator import FutureProjectionCalculator

def test_future_calculator():
    """Test the FutureProjectionCalculator class directly"""
    print("🧮 Testing FutureProjectionCalculator...")
    
    calculator = FutureProjectionCalculator()
    
    # Test with 12 months projection
    try:
        projection = calculator.calculate_projection(12)
        
        print(f"✅ Projection for 12 months:")
        print(f"   📊 Timeline: {projection['display_text']}")
        print(f"   🔴 Expense: {projection['base_projections']['expense']['formatted']}")
        print(f"   🟢 Saving: {projection['base_projections']['saving']['formatted']}")
        print(f"   🔵 Investment: {projection['base_projections']['investment']['formatted']}")
        print(f"   📊 Net: {projection['base_projections']['net']['formatted']}")
        
        print(f"\n💡 Scenarios ({len(projection['scenarios'])} found):")
        for scenario in projection['scenarios']:
            print(f"   - {scenario['title']}: {scenario['formatted']}")
        
        print(f"\n🎯 Goals ({len(projection['goals'])} found):")
        achievable_goals = [g for g in projection['goals'] if g['achievable']]
        print(f"   📈 Achievable goals: {len(achievable_goals)}")
        
        for goal in projection['goals'][:3]:  # Show top 3
            status = "✅" if goal['achievable'] else "❌"
            print(f"   {status} {goal['icon']} {goal['title']}: {goal['time_text']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing calculator: {e}")
        return False

def test_api_endpoints():
    """Test the API endpoints"""
    print("\n🌐 Testing API endpoints...")
    
    base_url = "http://127.0.0.1:8000"
    
    # Test future projection endpoint
    try:
        response = requests.get(f"{base_url}/api/future-projection/?months=6")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                projection_data = data['data']
                print(f"✅ Future projection API working")
                print(f"   📅 Timeline: {projection_data['display_text']}")
                print(f"   💰 Net projection: {projection_data['base_projections']['net']['formatted']}")
            else:
                print(f"❌ API returned error: {data.get('error')}")
                return False
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("⚠️  Server not running. Please start with: uv run python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False
    
    # Test monthly analysis endpoint
    try:
        current_date = datetime.now()
        response = requests.get(f"{base_url}/api/monthly-analysis/?year={current_date.year}&month={current_date.month}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                analysis_data = data['data']
                print(f"✅ Monthly analysis API working")
                print(f"   📊 {analysis_data['year']}-{analysis_data['month']:02d}")
                print(f"   💳 Transactions: {analysis_data['transaction_count']}")
                print(f"   💰 Net: {analysis_data['totals']['net']:,.0f}₫")
            else:
                print(f"❌ Monthly analysis API error: {data.get('error')}")
        else:
            print(f"❌ Monthly analysis API status {response.status_code}")
            
    except Exception as e:
        print(f"⚠️  Monthly analysis API test failed: {e}")
    
    return True

def test_sample_data():
    """Check if we have enough sample data for meaningful projections"""
    print("\n📊 Checking sample data...")
    
    # Check total transactions
    total_transactions = Transaction.objects.count()
    print(f"   📝 Total transactions: {total_transactions}")
    
    # Check by type
    expenses = Transaction.objects.filter(transaction_type='expense').count()
    savings = Transaction.objects.filter(transaction_type='saving').count()
    investments = Transaction.objects.filter(transaction_type='investment').count()
    
    print(f"   🔴 Expenses: {expenses}")
    print(f"   🟢 Savings: {savings}")
    print(f"   🔵 Investments: {investments}")
    
    # Check date range
    if total_transactions > 0:
        earliest = Transaction.objects.earliest('date').date
        latest = Transaction.objects.latest('date').date
        print(f"   📅 Date range: {earliest} to {latest}")
        
        # Check if we have recent data (last 30 days)
        recent_date = date.today() - timedelta(days=30)
        recent_transactions = Transaction.objects.filter(date__gte=recent_date).count()
        print(f"   🕐 Recent transactions (last 30 days): {recent_transactions}")
        
        if recent_transactions == 0:
            print("   ⚠️  No recent transactions found. Projections may not be very accurate.")
    
    return total_transactions > 0

def add_sample_data_if_needed():
    """Add some sample data if the database is empty or has insufficient data"""
    recent_date = date.today() - timedelta(days=30)
    recent_transactions = Transaction.objects.filter(date__gte=recent_date).count()
    
    if recent_transactions < 5:
        print("\n➕ Adding sample transactions for better testing...")
        
        sample_transactions = [
            # Expenses
            {'type': 'expense', 'amount': -50000, 'description': 'Ăn trưa', 'category': 'food', 'date': date.today() - timedelta(days=1)},
            {'type': 'expense', 'amount': -25000, 'description': 'Coffee Starbucks', 'category': 'coffee', 'date': date.today() - timedelta(days=2)},
            {'type': 'expense', 'amount': -200000, 'description': 'Xăng xe', 'category': 'transport', 'date': date.today() - timedelta(days=3)},
            {'type': 'expense', 'amount': -80000, 'description': 'Ăn tối', 'category': 'food', 'date': date.today() - timedelta(days=5)},
            {'type': 'expense', 'amount': -30000, 'description': 'Coffee Highland', 'category': 'coffee', 'date': date.today() - timedelta(days=7)},
            
            # Savings
            {'type': 'saving', 'amount': 500000, 'description': 'Tiết kiệm tháng', 'category': None, 'date': date.today() - timedelta(days=10)},
            {'type': 'saving', 'amount': 300000, 'description': 'Gửi ngân hàng', 'category': None, 'date': date.today() - timedelta(days=15)},
            
            # Investments
            {'type': 'investment', 'amount': 1000000, 'description': 'Mua VIC', 'category': None, 'date': date.today() - timedelta(days=20)},
            {'type': 'investment', 'amount': 500000, 'description': 'ETF VFMVN30', 'category': None, 'date': date.today() - timedelta(days=25)},
        ]
        
        created_count = 0
        for item in sample_transactions:
            transaction = Transaction.objects.create(
                transaction_type=item['type'],
                amount=item['amount'],
                description=item['description'],
                expense_category=item['category'],
                date=item['date']
            )
            created_count += 1
        
        print(f"   ✅ Added {created_count} sample transactions")
        return True
    
    return False

def main():
    """Main test function"""
    print("🔮 Phase 8: Future Me Simulator - Test Suite")
    print("=" * 50)
    
    # Check sample data
    has_data = test_sample_data()
    if not has_data:
        print("❌ No transaction data found. Adding sample data...")
        add_sample_data_if_needed()
    
    # Test calculator directly
    calculator_ok = test_future_calculator()
    
    # Test API endpoints
    api_ok = test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("📋 Test Summary:")
    print(f"   🧮 Calculator: {'✅ PASS' if calculator_ok else '❌ FAIL'}")
    print(f"   🌐 API: {'✅ PASS' if api_ok else '❌ FAIL'}")
    
    if calculator_ok and api_ok:
        print("\n🎉 All tests passed! Future Me Simulator is ready!")
        print("\n🚀 To test the full feature:")
        print("   1. Start server: uv run python manage.py runserver 8000")
        print("   2. Open browser: http://127.0.0.1:8000")
        print("   3. Click the '🔮 Future Me Simulator' button")
        print("   4. Try different timeline values with the slider")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
    
    return calculator_ok and api_ok

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 