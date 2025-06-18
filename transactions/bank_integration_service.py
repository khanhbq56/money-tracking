"""
Bank Integration Service
Coordinates Gmail API, email parsing, and transaction creation
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from django.utils import timezone
from django.conf import settings
from django.db import transaction as db_transaction

from .models import UserBankConfig, BankEmailTransaction, UserGmailPermission, Transaction
from .gmail_service import GmailService, BankEmailProcessor
from .bank_email_parser import BankEmailAIParser

logger = logging.getLogger(__name__)

class BankIntegrationService:
    """
    Main service coordinating bank email integration
    Handles the complete flow: Gmail API -> Email Parsing -> Transaction Creation
    """
    
    def __init__(self, user):
        """Initialize service for a specific user"""
        self.user = user
        self.parser = BankEmailAIParser(language=getattr(user, 'preferred_language', 'vi'))
    
    def sync_user_bank_emails(self, bank_code: str = None) -> Dict[str, Any]:
        """
        Sync bank emails for user's enabled banks
        
        Args:
            bank_code: Specific bank to sync, or None for all enabled banks
            
        Returns:
            Summary of sync results
        """
        try:
            # Get user's Gmail permission
            try:
                gmail_permission = UserGmailPermission.objects.get(user=self.user)
                if not gmail_permission.has_gmail_permission:
                    return {
                        'success': False,
                        'error': 'User does not have Gmail permission',
                        'requires_gmail_auth': True
                    }
            except UserGmailPermission.DoesNotExist:
                return {
                    'success': False,
                    'error': 'Gmail permission not found',
                    'requires_gmail_auth': True
                }
            
            # Get enabled bank configurations
            bank_configs = UserBankConfig.objects.filter(
                user=self.user,
                is_enabled=True
            )
            
            if bank_code:
                bank_configs = bank_configs.filter(bank_code=bank_code)
            
            if not bank_configs.exists():
                return {
                    'success': False,
                    'error': 'No enabled bank configurations found'
                }
            
            # Initialize Gmail service
            gmail_service = GmailService(gmail_permission)
            
            # Test Gmail connection
            if not gmail_service.test_connection():
                return {
                    'success': False,
                    'error': 'Gmail connection failed',
                    'requires_gmail_auth': True
                }
            
            # Sync each enabled bank
            sync_results = []
            total_new_emails = 0
            total_parsed_transactions = 0
            total_created_transactions = 0
            
            for bank_config in bank_configs:
                try:
                    result = self._sync_single_bank(gmail_service, bank_config)
                    sync_results.append(result)
                    
                    total_new_emails += result.get('new_emails_count', 0)
                    total_parsed_transactions += result.get('parsed_transactions_count', 0)
                    total_created_transactions += result.get('created_transactions_count', 0)
                    
                except Exception as e:
                    logger.error(f"Error syncing bank {bank_config.bank_code}: {str(e)}")
                    sync_results.append({
                        'bank_code': bank_config.bank_code,
                        'success': False,
                        'error': str(e)
                    })
            
            return {
                'success': True,
                'bank_results': sync_results,
                'summary': {
                    'total_new_emails': total_new_emails,
                    'total_parsed_transactions': total_parsed_transactions,
                    'total_created_transactions': total_created_transactions,
                    'banks_synced': len(sync_results)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in sync_user_bank_emails: {str(e)}")
            return {
                'success': False,
                'error': f'Sync failed: {str(e)}'
            }
    
    def _sync_single_bank(self, gmail_service: GmailService, bank_config: UserBankConfig) -> Dict[str, Any]:
        """
        Sync emails for a single bank configuration
        
        Args:
            gmail_service: Initialized Gmail service
            bank_config: Bank configuration to sync
            
        Returns:
            Sync result for this bank
        """
        try:
            logger.info(f"Starting sync for bank {bank_config.bank_code}")
            
            # Get bank sender emails
            sender_emails = BankEmailProcessor.get_bank_sender_emails(bank_config.bank_code)
            if not sender_emails:
                return {
                    'bank_code': bank_config.bank_code,
                    'success': False,
                    'error': f'No sender emails configured for {bank_config.bank_code}'
                }
            
            # Determine sync start date
            since_date = bank_config.last_sync_at or bank_config.sync_start_date
            if since_date:
                # Convert date to datetime for API
                if isinstance(since_date, datetime):
                    since_datetime = since_date
                else:
                    since_datetime = datetime.combine(since_date, datetime.min.time())
            else:
                # Default to last 7 days
                since_datetime = datetime.now() - timedelta(days=7)
            
            # Get emails from Gmail
            emails = gmail_service.get_bank_emails(sender_emails, since_datetime)
            
            # Filter for actual transaction emails
            transaction_emails = []
            for email in emails:
                if BankEmailProcessor.is_bank_transaction_email(email, bank_config.bank_code):
                    transaction_emails.append(email)
            
            logger.info(f"Found {len(transaction_emails)} transaction emails for {bank_config.bank_code}")
            
            # Check for already processed emails
            existing_email_ids = set(
                BankEmailTransaction.objects.filter(
                    user=self.user,
                    bank_config=bank_config
                ).values_list('email_message_id', flat=True)
            )
            
            new_emails = [
                email for email in transaction_emails
                if email.get('id') not in existing_email_ids
            ]
            
            logger.info(f"Processing {len(new_emails)} new emails for {bank_config.bank_code}")
            
            # Parse emails with AI
            user_context = {
                'account_suffix': bank_config.account_suffix,
                'bank_code': bank_config.bank_code
            }
            
            parsed_transactions = self.parser.parse_multiple_emails(
                new_emails, 
                bank_config.bank_code, 
                user_context
            )
            
            # Save parsed email transactions and create actual transactions
            created_transactions_count = 0
            
            for parsed_data in parsed_transactions:
                try:
                    # Create BankEmailTransaction record
                    bank_email_transaction = self._create_bank_email_transaction(
                        bank_config, parsed_data
                    )
                    
                    # Create actual Transaction if confidence is high enough
                    if parsed_data.get('ai_confidence', 0) >= 0.7:  # 70% confidence threshold
                        actual_transaction = self._create_actual_transaction(
                            bank_email_transaction, parsed_data
                        )
                        if actual_transaction:
                            bank_email_transaction.transaction_id = actual_transaction
                            bank_email_transaction.is_processed = True
                            bank_email_transaction.save()
                            created_transactions_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing parsed transaction: {str(e)}")
                    continue
            
            # Update bank config sync status
            bank_config.last_sync_at = timezone.now()
            bank_config.last_successful_sync = timezone.now()
            bank_config.sync_error_count = 0
            bank_config.last_sync_error = None
            bank_config.save()
            
            return {
                'bank_code': bank_config.bank_code,
                'success': True,
                'new_emails_count': len(new_emails),
                'parsed_transactions_count': len(parsed_transactions),
                'created_transactions_count': created_transactions_count,
                'last_sync_at': bank_config.last_sync_at.isoformat()
            }
            
        except Exception as e:
            # Update bank config with error
            bank_config.sync_error_count += 1
            bank_config.last_sync_error = str(e)
            bank_config.save()
            
            logger.error(f"Error syncing bank {bank_config.bank_code}: {str(e)}")
            return {
                'bank_code': bank_config.bank_code,
                'success': False,
                'error': str(e)
            }
    
    def _create_bank_email_transaction(self, bank_config: UserBankConfig, parsed_data: Dict[str, Any]) -> BankEmailTransaction:
        """Create BankEmailTransaction record from parsed data"""
        try:
            bank_email_transaction = BankEmailTransaction.objects.create(
                user=self.user,
                bank_config=bank_config,
                email_message_id=parsed_data['email_id'],
                email_date=parsed_data['email_date'],
                email_subject=parsed_data.get('email_subject', ''),
                transaction_type=parsed_data['transaction_type'],
                amount=parsed_data['amount'],
                description=parsed_data['description'],
                date=parsed_data['date'],
                expense_category=parsed_data.get('expense_category'),
                ai_confidence=parsed_data.get('ai_confidence', 0.5),
                parsing_method='gemini'
            )
            
            logger.info(f"Created BankEmailTransaction {bank_email_transaction.id}")
            return bank_email_transaction
            
        except Exception as e:
            logger.error(f"Error creating BankEmailTransaction: {str(e)}")
            raise
    
    def _create_actual_transaction(self, bank_email_transaction: BankEmailTransaction, parsed_data: Dict[str, Any]) -> Optional[Transaction]:
        """Create actual Transaction from parsed email data"""
        try:
            # Check for duplicate transactions based on amount, date, and description
            existing_transaction = Transaction.objects.filter(
                user=self.user,
                transaction_type=parsed_data['transaction_type'],
                amount=parsed_data['amount'],
                date=parsed_data['date'],
                description__icontains=parsed_data['description'][:20]  # Partial match
            ).first()
            
            if existing_transaction:
                logger.info(f"Duplicate transaction found, linking to existing {existing_transaction.id}")
                return existing_transaction
            
            # Create new transaction
            transaction = Transaction.objects.create(
                user=self.user,
                transaction_type=parsed_data['transaction_type'],
                amount=parsed_data['amount'],
                description=f"[Bank] {parsed_data['description']}",  # Mark as bank import
                date=parsed_data['date'],
                expense_category=parsed_data.get('expense_category'),
                ai_confidence=parsed_data.get('ai_confidence', 0.5)
            )
            
            logger.info(f"Created Transaction {transaction.id} from bank email")
            return transaction
            
        except Exception as e:
            logger.error(f"Error creating Transaction: {str(e)}")
            return None
    
    def get_sync_history(self, bank_code: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get sync history for user's bank integrations
        
        Args:
            bank_code: Specific bank or None for all
            limit: Maximum number of records to return
            
        Returns:
            List of sync history records
        """
        try:
            query = BankEmailTransaction.objects.filter(user=self.user)
            
            if bank_code:
                query = query.filter(bank_config__bank_code=bank_code)
            
            email_transactions = query.order_by('-email_date')[:limit]
            
            history = []
            for et in email_transactions:
                history.append({
                    'id': et.id,
                    'bank_code': et.bank_config.bank_code,
                    'email_date': et.email_date.isoformat(),
                    'email_subject': et.email_subject,
                    'transaction_type': et.transaction_type,
                    'amount': float(et.amount),
                    'description': et.description,
                    'date': et.date.isoformat(),
                    'ai_confidence': et.ai_confidence,
                    'is_processed': et.is_processed,
                    'has_transaction': et.transaction_id is not None,
                    'created_at': et.created_at.isoformat()
                })
            
            return history
            
        except Exception as e:
            logger.error(f"Error getting sync history: {str(e)}")
            return []
    
    def test_bank_integration(self, bank_code: str) -> Dict[str, Any]:
        """
        Test bank integration with sample data
        
        Args:
            bank_code: Bank to test
            
        Returns:
            Test results
        """
        try:
            # Test AI parser
            parser_test = self.parser.test_parsing_with_sample(bank_code)
            
            # Test Gmail configuration
            try:
                gmail_permission = UserGmailPermission.objects.get(user=self.user)
                gmail_service = GmailService(gmail_permission)
                gmail_connected = gmail_service.test_connection()
            except Exception:
                gmail_connected = False
            
            # Test bank configuration
            try:
                bank_config = UserBankConfig.objects.get(
                    user=self.user,
                    bank_code=bank_code,
                    is_enabled=True
                )
                bank_configured = True
            except UserBankConfig.DoesNotExist:
                bank_configured = False
            
            return {
                'bank_code': bank_code,
                'ai_parser_test': parser_test,
                'gmail_connected': gmail_connected,
                'bank_configured': bank_configured,
                'ready_for_sync': all([
                    parser_test.get('success', False),
                    gmail_connected,
                    bank_configured
                ])
            }
            
        except Exception as e:
            logger.error(f"Error testing bank integration: {str(e)}")
            return {
                'bank_code': bank_code,
                'error': str(e),
                'ready_for_sync': False
            } 