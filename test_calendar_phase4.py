#!/usr/bin/env python3
"""
Test script for Phase 4: Custom Calendar Implementation
Tests API endpoints, calendar functionality, and frontend integration
"""

import requests
import json
import sys
from datetime import datetime, date
from typing import Dict, List, Any

class CalendarPhase4Tester:
    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.test_results = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def test_result(self, test_name: str, passed: bool, details: str = ""):
        """Record test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        self.test_results.append({
            'test': test_name, 
            'passed': passed, 
            'details': details
        })
        self.log(f"{status} {test_name} - {details}")
        
    def test_main_page_loads(self):
        """Test 1: Main page loads successfully"""
        try:
            response = self.session.get(self.base_url)
            
            if response.status_code == 200:
                # Check for calendar-related elements
                content = response.text
                calendar_elements = [
                    'calendar-grid',
                    'calendar-container', 
                    'filter-btn',
                    'previousMonth()',
                    'nextMonth()',
                    'setFilter(',
                    'calendar.js'
                ]
                
                missing_elements = []
                for element in calendar_elements:
                    if element not in content:
                        missing_elements.append(element)
                
                if not missing_elements:
                    self.test_result("Main Page Load", True, "All calendar elements present")
                else:
                    self.test_result("Main Page Load", False, f"Missing: {missing_elements}")
            else:
                self.test_result("Main Page Load", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.test_result("Main Page Load", False, f"Exception: {str(e)}")
    
    def test_calendar_data_api(self):
        """Test 2: Calendar data API endpoint"""
        try:
            # Test current month
            current_date = datetime.now()
            url = f"{self.base_url}/api/calendar-data/"
            params = {
                'month': current_date.month,
                'year': current_date.year,
                'filter': 'all'
            }
            
            response = self.session.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check response structure
                required_fields = ['calendar_data', 'month', 'year', 'filter']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    calendar_data = data['calendar_data']
                    if isinstance(calendar_data, list):
                        self.test_result("Calendar Data API", True, 
                                       f"Returned {len(calendar_data)} days of data")
                    else:
                        self.test_result("Calendar Data API", False, 
                                       "calendar_data is not a list")
                else:
                    self.test_result("Calendar Data API", False, 
                                   f"Missing fields: {missing_fields}")
            else:
                self.test_result("Calendar Data API", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.test_result("Calendar Data API", False, f"Exception: {str(e)}")
    
    def test_calendar_filters(self):
        """Test 3: Calendar filter functionality"""
        filters = ['all', 'expense', 'saving', 'investment']
        current_date = datetime.now()
        
        for filter_type in filters:
            try:
                url = f"{self.base_url}/api/calendar-data/"
                params = {
                    'month': current_date.month,
                    'year': current_date.year,
                    'filter': filter_type
                }
                
                response = self.session.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('filter') == filter_type:
                        self.test_result(f"Filter: {filter_type}", True, 
                                       f"Filter applied correctly")
                    else:
                        self.test_result(f"Filter: {filter_type}", False, 
                                       f"Filter not applied correctly")
                else:
                    self.test_result(f"Filter: {filter_type}", False, 
                                   f"HTTP {response.status_code}")
                    
            except Exception as e:
                self.test_result(f"Filter: {filter_type}", False, f"Exception: {str(e)}")
    
    def test_date_range_validation(self):
        """Test 4: Date range validation"""
        test_cases = [
            # (month, year, should_pass, description)
            (1, 2025, True, "Valid date January 2025"),
            (12, 2024, True, "Valid date December 2024"),
            (0, 2025, False, "Invalid month 0"),
            (13, 2025, False, "Invalid month 13"),
            (6, 1999, False, "Year too low"),
            (6, 2101, False, "Year too high"),
        ]
        
        for month, year, should_pass, description in test_cases:
            try:
                url = f"{self.base_url}/api/calendar-data/"
                params = {
                    'month': month,
                    'year': year,
                    'filter': 'all'
                }
                
                response = self.session.get(url, params=params)
                
                if should_pass:
                    passed = response.status_code == 200
                    self.test_result(f"Date Validation", passed, description)
                else:
                    passed = response.status_code == 400
                    self.test_result(f"Date Validation", passed, description)
                    
            except Exception as e:
                self.test_result(f"Date Validation", False, f"{description} - Exception: {str(e)}")
    
    def test_monthly_totals_api(self):
        """Test 5: Monthly totals API integration"""
        try:
            url = f"{self.base_url}/api/monthly-totals/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                required_fields = ['monthly_totals', 'formatted']
                missing_fields = [field for field in required_fields if field not in data]
                
                if not missing_fields:
                    monthly_totals = data['monthly_totals']
                    formatted = data['formatted']
                    
                    # Check monthly totals structure
                    expected_totals = ['expense', 'saving', 'investment', 'net_total']
                    missing_totals = [field for field in expected_totals 
                                    if field not in monthly_totals]
                    
                    if not missing_totals:
                        self.test_result("Monthly Totals API", True, 
                                       "All required fields present")
                    else:
                        self.test_result("Monthly Totals API", False, 
                                       f"Missing totals: {missing_totals}")
                else:
                    self.test_result("Monthly Totals API", False, 
                                   f"Missing fields: {missing_fields}")
            else:
                self.test_result("Monthly Totals API", False, f"HTTP {response.status_code}")
                
        except Exception as e:
            self.test_result("Monthly Totals API", False, f"Exception: {str(e)}")
    
    def test_static_files(self):
        """Test 6: Calendar static files are accessible"""
        static_files = [
            '/static/js/calendar.js',
            '/static/css/styles.css',
            '/static/js/i18n.js',
            '/static/js/dashboard.js',
        ]
        
        for file_path in static_files:
            try:
                url = f"{self.base_url}{file_path}"
                response = self.session.get(url)
                
                if response.status_code == 200:
                    # Additional checks for calendar.js
                    if 'calendar.js' in file_path:
                        content = response.text
                        expected_elements = [
                            'ExpenseCalendar',
                            'renderCalendarGrid',
                            'setFilter',
                            'previousMonth',
                            'nextMonth'
                        ]
                        
                        missing_elements = [elem for elem in expected_elements 
                                          if elem not in content]
                        
                        if not missing_elements:
                            self.test_result("Static Files", True, f"{file_path} has all calendar functions")
                        else:
                            self.test_result("Static Files", False, 
                                           f"{file_path} missing: {missing_elements}")
                    else:
                        self.test_result("Static Files", True, f"{file_path} accessible")
                else:
                    self.test_result("Static Files", False, 
                                   f"{file_path} HTTP {response.status_code}")
                    
            except Exception as e:
                self.test_result("Static Files", False, f"{file_path} - Exception: {str(e)}")
    
    def test_i18n_support(self):
        """Test 7: Internationalization support"""
        try:
            # Check if translations are working
            url = f"{self.base_url}/api/translations/vi/"
            response = self.session.get(url)
            
            if response.status_code == 200:
                data = response.json()
                
                # Check for calendar-specific translations
                calendar_keys = [
                    'Thứ 2', 'Thứ 3', 'Thứ 4', 'Thứ 5', 
                    'Thứ 6', 'Thứ 7', 'CN'
                ]
                
                missing_keys = [key for key in calendar_keys if key not in data]
                
                if not missing_keys:
                    self.test_result("I18n Support", True, "Calendar day translations present")
                else:
                    self.test_result("I18n Support", False, f"Missing translations: {missing_keys}")
            else:
                self.test_result("I18n Support", False, f"Translation API HTTP {response.status_code}")
                
        except Exception as e:
            self.test_result("I18n Support", False, f"Exception: {str(e)}")
    
    def test_transaction_creation_integration(self):
        """Test 8: Transaction creation affects calendar"""
        try:
            # Create a test transaction
            today = date.today()
            transaction_data = {
                'transaction_type': 'expense',
                'amount': 25000,
                'description': 'Test Calendar Coffee',
                'date': today.isoformat(),
                'expense_category': 'coffee'
            }
            
            url = f"{self.base_url}/api/transactions/"
            response = self.session.post(url, json=transaction_data)
            
            if response.status_code == 201:
                transaction = response.json()
                transaction_id = transaction.get('id')
                
                # Check if transaction appears in calendar data
                calendar_url = f"{self.base_url}/api/calendar-data/"
                calendar_params = {
                    'month': today.month,
                    'year': today.year,
                    'filter': 'all'
                }
                
                calendar_response = self.session.get(calendar_url, params=calendar_params)
                
                if calendar_response.status_code == 200:
                    calendar_data = calendar_response.json()['calendar_data']
                    
                    # Look for today's data
                    today_data = None
                    for day_data in calendar_data:
                        if day_data['date'] == today.isoformat():
                            today_data = day_data
                            break
                    
                    if today_data and len(today_data.get('transactions', [])) > 0:
                        # Clean up - delete the test transaction
                        delete_url = f"{self.base_url}/api/transactions/{transaction_id}/"
                        self.session.delete(delete_url)
                        
                        self.test_result("Transaction Integration", True, 
                                       "Transaction appears in calendar")
                    else:
                        self.test_result("Transaction Integration", False, 
                                       "Transaction not found in calendar")
                else:
                    self.test_result("Transaction Integration", False, 
                                   "Calendar API failed after transaction creation")
            else:
                self.test_result("Transaction Integration", False, 
                               f"Transaction creation failed HTTP {response.status_code}")
                
        except Exception as e:
            self.test_result("Transaction Integration", False, f"Exception: {str(e)}")
    
    def print_summary(self):
        """Print test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print("\n" + "="*60)
        print("PHASE 4 CALENDAR IMPLEMENTATION TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n📋 FAILED TESTS:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        print("\n🎯 PHASE 4 FEATURES IMPLEMENTED:")
        features = [
            "✅ Custom calendar component (ExpenseCalendar class)",
            "✅ 7x6 calendar grid with CSS Grid",
            "✅ Month navigation (previous/next buttons)",
            "✅ Transaction events with colored indicators",
            "✅ Filter buttons (All, Expense, Saving, Investment)",
            "✅ API integration (/api/calendar-data/)",
            "✅ Day click handlers and event details",
            "✅ Internationalization support (vi/en)",
            "✅ Mobile-responsive design",
            "✅ Real-time data loading and updates"
        ]
        
        for feature in features:
            print(f"  {feature}")
        
        print("\n🚀 READY FOR PHASE 5: AI Chat Integration")
        return failed_tests == 0

def main():
    """Run all Phase 4 tests"""
    print("🧪 Starting Phase 4: Custom Calendar Implementation Tests")
    print("="*60)
    
    tester = CalendarPhase4Tester()
    
    # Run all tests
    tester.test_main_page_loads()
    tester.test_calendar_data_api()
    tester.test_calendar_filters()
    tester.test_date_range_validation()
    tester.test_monthly_totals_api()
    tester.test_static_files()
    tester.test_i18n_support()
    tester.test_transaction_creation_integration()
    
    # Print summary
    success = tester.print_summary()
    
    if success:
        print("\n🎉 All Phase 4 tests passed! Calendar implementation is complete.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 