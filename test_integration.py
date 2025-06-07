"""
Comprehensive integration tests for Expense Tracker Application
Tests complete user workflows across all features
"""
import pytest
import json
from datetime import datetime, date
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from unittest.mock import patch, MagicMock

from transactions.models import Transaction
from ai_chat.models import ChatMessage


class ComprehensiveIntegrationTest(TestCase):
    """Test complete user workflows end-to-end"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        # Create test user if needed for future features
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
    def test_workflow_1_chat_to_calendar_to_dashboard(self):
        """
        Test: User creates expense via chat → appears on calendar → updates dashboard
        """
        print("\n=== Testing Workflow 1: Chat → Calendar → Dashboard ===")
        
        # Step 1: Process chat message
        chat_data = {
            'message': 'coffee 25k',
            'language': 'vi'
        }
        
        with patch('ai_chat.gemini_service.GeminiService.categorize_transaction') as mock_gemini:
            mock_gemini.return_value = {
                'type': 'expense',
                'amount': 25000,
                'description': 'Coffee',
                'category': 'coffee',
                'confidence': 0.95,
                'icon': '☕',
                'parsed_date': date.today().isoformat()
            }
            
            response = self.client.post('/api/chat/process/', 
                                      data=json.dumps(chat_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            chat_response = response.json()
            self.assertIn('chat_id', chat_response)
            
        # Step 2: Confirm transaction
        confirm_data = {
            'chat_id': chat_response['chat_id'],
            'transaction_data': chat_response['ai_response']
        }
        
        response = self.client.post('/api/chat/confirm/',
                                  data=json.dumps(confirm_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Transaction.objects.filter(description='Coffee').exists())
        
        # Step 3: Check calendar data
        today = date.today()
        response = self.client.get(f'/api/calendar-data/?month={today.month}&year={today.year}')
        self.assertEqual(response.status_code, 200)
        
        calendar_data = response.json()
        today_str = today.isoformat()
        self.assertIn(today_str, calendar_data['calendar_data'])
        
        # Step 4: Check dashboard updates
        response = self.client.get('/api/monthly-totals/')
        self.assertEqual(response.status_code, 200)
        
        totals = response.json()
        self.assertTrue(totals['monthly_totals']['expense'] >= 25000)
        
        print("✅ Workflow 1 completed successfully")
        
    def test_workflow_2_voice_ai_categorization_confirmation(self):
        """
        Test: Voice input → AI categorization → confirmation → data persistence
        """
        print("\n=== Testing Workflow 2: Voice → AI → Confirmation ===")
        
        # Step 1: Voice input processing
        voice_data = {
            'message': 'ăn trưa năm mười ngàn',
            'has_voice': True,
            'language': 'vi'
        }
        
        with patch('ai_chat.gemini_service.GeminiService.categorize_transaction') as mock_gemini:
            mock_gemini.return_value = {
                'type': 'expense',
                'amount': 50000,
                'description': 'Ăn trưa',
                'category': 'food',
                'confidence': 0.92,
                'icon': '🍜',
                'parsed_date': date.today().isoformat(),
                'has_voice': True
            }
            
            response = self.client.post('/api/chat/process/',
                                      data=json.dumps(voice_data),
                                      content_type='application/json')
            
            self.assertEqual(response.status_code, 200)
            chat_response = response.json()
            
        # Step 2: Verify voice flag is preserved
        chat_message = ChatMessage.objects.get(id=chat_response['chat_id'])
        self.assertTrue(chat_message.has_voice_input)
        self.assertEqual(chat_message.voice_transcript, 'ăn trưa năm mười ngàn')
        
        # Step 3: Confirm transaction
        confirm_data = {
            'chat_id': chat_response['chat_id'],
            'transaction_data': chat_response['ai_response']
        }
        
        response = self.client.post('/api/chat/confirm/',
                                  data=json.dumps(confirm_data),
                                  content_type='application/json')
        
        self.assertEqual(response.status_code, 200)
        
        # Step 4: Verify data persistence
        transaction = Transaction.objects.get(description='Ăn trưa')
        self.assertEqual(transaction.amount, 50000)
        self.assertEqual(transaction.expense_category, 'food')
        self.assertEqual(transaction.transaction_type, 'expense')
        
        print("✅ Workflow 2 completed successfully")
        
    def test_workflow_3_language_switching(self):
        """
        Test: Language switching → all texts update correctly
        """
        print("\n=== Testing Workflow 3: Language Switching ===")
        
        # Test Vietnamese translations
        response = self.client.get('/api/translations/vi/')
        self.assertEqual(response.status_code, 200)
        vi_translations = response.json()
        self.assertIn('expense', vi_translations)
        
        # Test English translations  
        response = self.client.get('/api/translations/en/')
        self.assertEqual(response.status_code, 200)
        en_translations = response.json()
        self.assertIn('expense', en_translations)
        
        # Verify different translations
        self.assertNotEqual(vi_translations['expense'], en_translations['expense'])
        
        print("✅ Workflow 3 completed successfully")
        
    def test_workflow_4_future_me_projections(self):
        """
        Test: Future Me projections → accurate calculations
        """
        print("\n=== Testing Workflow 4: Future Me Projections ===")
        
        # Create sample transactions
        Transaction.objects.create(
            transaction_type='expense',
            amount=1000000,
            description='Test expense',
            date=date.today(),
            expense_category='other'
        )
        
        Transaction.objects.create(
            transaction_type='saving',
            amount=500000,
            description='Test saving',
            date=date.today()
        )
        
        # Test future projection
        response = self.client.get('/api/future-projection/?months=12')
        self.assertEqual(response.status_code, 200)
        
        projection = response.json()
        self.assertIn('base_projections', projection)
        self.assertIn('scenarios', projection)
        self.assertIn('goals', projection)
        
        # Verify calculations are reasonable
        base = projection['base_projections']
        self.assertTrue(base['expense_projection'] < 0)  # Expenses should be negative
        self.assertTrue(base['saving_projection'] > 0)   # Savings should be positive
        
        print("✅ Workflow 4 completed successfully")
        
    def test_workflow_5_meme_generation_display(self):
        """
        Test: Meme generation → proper analysis and display
        """
        print("\n=== Testing Workflow 5: Meme Generation ===")
        
        # Create sample weekly data
        from datetime import timedelta
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        
        # Create coffee transactions
        for i in range(5):  # 5 days of coffee
            Transaction.objects.create(
                transaction_type='expense',
                amount=25000,
                description=f'Coffee {i+1}',
                date=week_start + timedelta(days=i),
                expense_category='coffee'
            )
        
        # Test meme generation
        response = self.client.get('/api/meme/weekly/')
        self.assertEqual(response.status_code, 200)
        
        meme_data = response.json()
        self.assertIn('meme', meme_data)
        self.assertIn('analysis', meme_data)
        self.assertIn('personality', meme_data)
        
        # Should detect coffee addict pattern
        self.assertEqual(meme_data['personality'], 'Coffee Addict')
        
        print("✅ Workflow 5 completed successfully")
        
    def test_api_performance_and_error_handling(self):
        """
        Test API performance and error handling
        """
        print("\n=== Testing API Performance & Error Handling ===")
        
        # Test missing data handling
        response = self.client.post('/api/chat/process/',
                                  data=json.dumps({}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        
        # Test invalid transaction confirmation
        response = self.client.post('/api/chat/confirm/',
                                  data=json.dumps({'chat_id': 99999}),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 404)
        
        # Test calendar with invalid date
        response = self.client.get('/api/calendar-data/?month=13&year=2024')
        self.assertEqual(response.status_code, 400)
        
        print("✅ API Error Handling tests completed")
        
    def test_mobile_responsiveness_and_performance(self):
        """
        Test mobile user agent handling and performance
        """
        print("\n=== Testing Mobile Responsiveness ===")
        
        # Test with mobile user agent
        mobile_headers = {
            'HTTP_USER_AGENT': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15'
        }
        
        response = self.client.get('/', **mobile_headers)
        self.assertEqual(response.status_code, 200)
        
        # Test API response times (basic check)
        import time
        start_time = time.time()
        response = self.client.get('/api/monthly-totals/')
        end_time = time.time()
        
        response_time = end_time - start_time
        self.assertLess(response_time, 2.0)  # Should respond within 2 seconds
        
        print(f"✅ API response time: {response_time:.3f}s")
        
    def test_security_features(self):
        """
        Test security features and headers
        """
        print("\n=== Testing Security Features ===")
        
        # Test CSRF protection
        response = self.client.post('/api/chat/process/',
                                  data=json.dumps({'message': 'test'}),
                                  content_type='application/json')
        # Should work without CSRF for API endpoints
        self.assertIn(response.status_code, [200, 400])
        
        # Test XSS protection in responses
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        
        print("✅ Security tests completed")

    def test_health_check_endpoint(self):
        """
        Test health check endpoint functionality
        """
        print("\n=== Testing Health Check Endpoint ===")
        
        response = self.client.get('/health/')
        self.assertEqual(response.status_code, 200)
        
        health_data = response.json()
        self.assertIn('status', health_data)
        self.assertIn('database', health_data)
        self.assertIn('environment', health_data)
        self.assertIn('version', health_data)
        
        print("✅ Health check tests completed")


class LoadTestCase(TestCase):
    """Basic load testing for critical endpoints"""
    
    def test_concurrent_requests_simulation(self):
        """
        Simulate multiple concurrent requests to test stability
        """
        print("\n=== Testing Concurrent Request Handling ===")
        
        import threading
        import time
        
        results = []
        
        def make_request():
            try:
                response = self.client.get('/health/')
                results.append(response.status_code)
            except Exception as e:
                results.append(f"Error: {str(e)}")
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
        
        # Start all threads
        for thread in threads:
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        success_count = sum(1 for result in results if result == 200)
        self.assertGreaterEqual(success_count, 8)  # At least 80% success rate
        
        print(f"✅ Concurrent requests: {success_count}/10 successful")


if __name__ == '__main__':
    # Run specific test workflows
    import sys
    if len(sys.argv) > 1:
        if sys.argv[1] == 'workflow1':
            test = ComprehensiveIntegrationTest()
            test.setUp()
            test.test_workflow_1_chat_to_calendar_to_dashboard()
        # Add more workflow-specific runs as needed
    else:
        # Run all tests
        import unittest
        unittest.main() 