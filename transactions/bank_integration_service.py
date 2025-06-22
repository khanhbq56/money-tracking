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
from .currency_service import CurrencyService

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
        self.currency_service = CurrencyService()
    
    def sync_user_bank_emails(self, bank_code: str = None, **sync_options) -> Dict[str, Any]:
        """
        Sync bank emails for user's enabled banks with flexible options
        
        Args:
            bank_code: Specific bank to sync, or None for all enabled banks
            **sync_options: Additional sync parameters:
                - sync_date: Specific date (YYYY-MM-DD) to sync
                - sync_year, sync_month: Specific month to sync
                - from_date, to_date: Date range to sync
                - sync_all: Sync all available emails
                - force_refresh: Reprocess existing emails
            
        Returns:
            Summary of sync results
        """
        logger.info(f"🎯 sync_user_bank_emails called for user {self.user.email}")
        logger.info(f"📋 Parameters - bank_code: {bank_code}, options: {sync_options}")
        
        try:
            # Get user's Gmail permission
            logger.info(f"🔐 Checking Gmail permission for user {self.user.email}")
            try:
                gmail_permission = UserGmailPermission.objects.get(user=self.user)
                logger.info(f"✅ Gmail permission found: has_permission={gmail_permission.has_gmail_permission}")
                if not gmail_permission.has_gmail_permission:
                    logger.warning(f"❌ User {self.user.email} does not have Gmail permission")
                    return {
                        'success': False,
                        'error': 'User does not have Gmail permission',
                        'requires_gmail_auth': True
                    }
            except UserGmailPermission.DoesNotExist:
                logger.warning(f"❌ No Gmail permission record found for user {self.user.email}")
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
            
            # Sync each enabled bank with custom options
            sync_results = []
            for bank_config in bank_configs:
                result = self._sync_single_bank_with_options(gmail_service, bank_config, sync_options)
                sync_results.append(result)
            
            # Calculate overall success
            successful_syncs = [r for r in sync_results if r.get('success', False)]
            overall_success = len(successful_syncs) > 0
            
            return {
                'success': overall_success,
                'data': sync_results,
                'total_banks': len(sync_results),
                'successful_banks': len(successful_syncs)
            }
            
        except Exception as e:
            logger.error(f"Error in sync_user_bank_emails: {str(e)}")
            return {
                'success': False,
                'error': f'Sync service error: {str(e)}'
            }
    
    def _sync_single_bank_with_options(self, gmail_service: GmailService, bank_config: UserBankConfig, sync_options: Dict[str, Any]) -> Dict[str, Any]:
        """
        Sync emails for a single bank configuration with custom options
        
        Args:
            gmail_service: Initialized Gmail service
            bank_config: Bank configuration to sync
            sync_options: Additional sync parameters
            
        Returns:
            Sync result for this bank
        """
        try:
            logger.info(f"Starting sync for bank {bank_config.bank_code} with options: {sync_options}")
            
            # Get bank sender emails (support custom banks)
            sender_emails = BankEmailProcessor.get_bank_sender_emails(bank_config.bank_code, bank_config)
            if not sender_emails:
                return {
                    'bank_code': bank_config.bank_code,
                    'success': False,
                    'error': f'No sender emails configured for {bank_config.bank_code}'
                }
            
            # Determine sync date range based on options
            since_datetime, until_datetime = self._calculate_sync_date_range(bank_config, sync_options)
            
            logger.info(f"Syncing {bank_config.bank_code} from {since_datetime} to {until_datetime or 'now'}")
            
            # Get emails from Gmail with date range
            emails = gmail_service.get_bank_emails(sender_emails, since_datetime, until_datetime)
            
            # Filter for actual transaction emails
            transaction_emails = []
            for email in emails:
                if BankEmailProcessor.is_bank_transaction_email(email, bank_config.bank_code):
                    transaction_emails.append(email)
            
            logger.info(f"Found {len(transaction_emails)} transaction emails for {bank_config.bank_code}")
            
            # Handle force refresh option
            force_refresh = sync_options.get('force_refresh', False)
            if force_refresh:
                # Delete existing email records in the date range to reprocess
                self._clear_existing_email_records(bank_config, since_datetime, until_datetime)
                logger.info(f"Force refresh enabled - cleared existing records for {bank_config.bank_code}")
            
            # Check for already processed emails (unless force refresh)
            existing_email_ids = set()
            if not force_refresh:
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
            
            logger.info(f"Starting AI parsing for {len(new_emails)} emails from {bank_config.bank_code}")
            
            # Log sample email for debugging
            if new_emails:
                logger.warning(f"📧 DEBUG: Sample email content (first 500 chars): {new_emails[0].get('body', '')[:500]}...")
                logger.warning(f"📧 DEBUG: Email subject: {new_emails[0].get('subject', 'No subject')}")
            else:
                logger.warning(f"📧 DEBUG: No new emails found for parsing!")
            
            parsed_transactions = self.parser.parse_multiple_emails(
                new_emails, 
                bank_config.bank_code, 
                user_context
            )
            
            logger.info(f"AI parsing results: {len(parsed_transactions)} transactions found from {len(new_emails)} emails")
            
            # Save parsed email transactions and create actual transactions
            created_transactions_count = 0
            
            for parsed_data in parsed_transactions:
                try:
                    # Create BankEmailTransaction record
                    bank_email_transaction = self._create_bank_email_transaction(
                        bank_config, parsed_data
                    )
                    
                    # Create actual Transaction if confidence is high enough
                    confidence = parsed_data.get('ai_confidence', 0)
                    logger.info(f"Transaction confidence: {confidence}")
                    
                    if confidence >= 0.3:  # Lowered to 30% confidence threshold - accepting even uncertain transactions
                        actual_transaction = self._create_actual_transaction(
                            bank_email_transaction, parsed_data
                        )
                        if actual_transaction:
                            bank_email_transaction.transaction_id = actual_transaction
                            bank_email_transaction.is_processed = True
                            bank_email_transaction.save()
                            created_transactions_count += 1
                            logger.info(f"✅ Created transaction {actual_transaction.id}")
                    else:
                        logger.warning(f"⚠️ Transaction skipped due to low confidence: {confidence}")
                    
                except Exception as e:
                    logger.error(f"Error processing parsed transaction: {str(e)}")
                    continue
            
            # Update bank config sync status
            bank_config.last_sync_at = timezone.now()
            if created_transactions_count > 0:
                bank_config.last_successful_sync = timezone.now()
                bank_config.sync_error_count = 0
                bank_config.last_sync_error = None
            bank_config.save()
            
            # Create detailed summary message
            summary_msg = f"📊 Sync complete for {bank_config.bank_code.upper()}: "
            summary_msg += f"📧 {len(new_emails)} emails checked, "
            summary_msg += f"💳 {len(parsed_transactions)} transactions found, "
            summary_msg += f"✅ {created_transactions_count} imported"
            
            if len(new_emails) > 0 and len(parsed_transactions) == 0:
                summary_msg += " (No transaction emails found - this is normal for promotional emails)"
            
            logger.info(summary_msg)
            
            return {
                'bank_code': bank_config.bank_code,
                'success': True,
                'new_emails_count': len(new_emails),
                'parsed_transactions_count': len(parsed_transactions),
                'created_transactions_count': created_transactions_count,
                'last_sync_at': bank_config.last_sync_at.isoformat(),
                'sync_date_range': {
                    'from': since_datetime.isoformat(),
                    'to': until_datetime.isoformat() if until_datetime else None
                },
                'summary': summary_msg
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
    
    def _calculate_sync_date_range(self, bank_config: UserBankConfig, sync_options: Dict[str, Any]) -> tuple:
        """Calculate sync date range based on options with timezone awareness"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        
        # Handle sync_all option
        if sync_options.get('sync_all', False):
            # Sync all available emails (last 2 years)
            since_datetime = timezone.now() - timedelta(days=730)
            until_datetime = None
            return since_datetime, until_datetime
        
        # Handle specific date option
        if sync_options.get('sync_date'):
            sync_date_str = sync_options['sync_date']
            sync_date = datetime.strptime(sync_date_str, '%Y-%m-%d').date()
            since_datetime = timezone.make_aware(datetime.combine(sync_date, datetime.min.time()))
            until_datetime = timezone.make_aware(datetime.combine(sync_date, datetime.max.time()))
            return since_datetime, until_datetime
        
        # Handle specific month option
        if sync_options.get('sync_year') and sync_options.get('sync_month'):
            year = int(sync_options['sync_year'])
            month = int(sync_options['sync_month'])
            
            # First day of the month
            since_datetime = timezone.make_aware(datetime(year, month, 1))
            
            # Last day of the month
            if month == 12:
                until_datetime = timezone.make_aware(datetime(year + 1, 1, 1) - timedelta(seconds=1))
            else:
                until_datetime = timezone.make_aware(datetime(year, month + 1, 1) - timedelta(seconds=1))
            
            return since_datetime, until_datetime
        
        # Handle date range option
        if sync_options.get('from_date') and sync_options.get('to_date'):
            from_date_str = sync_options['from_date']
            to_date_str = sync_options['to_date']
            
            from_date = datetime.strptime(from_date_str, '%Y-%m-%d').date()
            to_date = datetime.strptime(to_date_str, '%Y-%m-%d').date()
            
            since_datetime = timezone.make_aware(datetime.combine(from_date, datetime.min.time()))
            until_datetime = timezone.make_aware(datetime.combine(to_date, datetime.max.time()))
            
            return since_datetime, until_datetime
        
        # Default to recent emails (last 7 days) or last sync
        since_date = bank_config.last_sync_at or bank_config.sync_start_date
        if since_date:
            # Convert date to timezone-aware datetime for API
            if isinstance(since_date, datetime):
                since_datetime = since_date if since_date.tzinfo else timezone.make_aware(since_date)
            else:
                since_datetime = timezone.make_aware(datetime.combine(since_date, datetime.min.time()))
        else:
            # Default to last 7 days
            since_datetime = timezone.now() - timedelta(days=7)
        
        logger.info(f"Calculated sync range: from {since_datetime} to {None}")
        return since_datetime, None
    
    def _clear_existing_email_records(self, bank_config: UserBankConfig, since_datetime: datetime, until_datetime: datetime = None):
        """Clear existing email records in date range for force refresh"""
        query = BankEmailTransaction.objects.filter(
            user=self.user,
            bank_config=bank_config,
            email_date__gte=since_datetime
        )
        
        if until_datetime:
            query = query.filter(email_date__lte=until_datetime)
        
        deleted_count = query.delete()[0]
        logger.info(f"Deleted {deleted_count} existing email records for force refresh")
        
        return deleted_count
    
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
        """Create actual Transaction from parsed email data with currency conversion"""
        try:
            # Apply currency conversion if needed
            original_amount = parsed_data['amount']
            original_currency = parsed_data.get('currency', 'VND')
            description = parsed_data.get('description', '')
            
            # Convert to VND if transaction is in USD
            if original_currency == 'USD':
                vnd_amount = self.currency_service.convert_usd_to_vnd(original_amount)
                if vnd_amount:
                    final_amount = vnd_amount
                    exchange_rate = self.currency_service.get_usd_to_vnd_rate()
                    final_description = f"[Bank] {description} (${original_amount:.2f} USD → {final_amount:,.0f}₫ @ {exchange_rate:,.0f})"
                    logger.info(f"💱 ${original_amount} USD → {final_amount:,.0f} VND @ {exchange_rate:,.0f}")
                else:
                    # Fallback if conversion fails
                    final_amount = original_amount * 24000  # Approximate rate
                    final_description = f"[Bank] {description} (${original_amount:.2f} USD → {final_amount:,.0f}₫ @ ~24,000)"
                    logger.warning(f"💱 Currency conversion failed, using fallback rate")
            else:
                # Already in VND, no conversion needed
                final_amount = original_amount
                final_description = f"[Bank] {description}"
            
            # Check for duplicate transactions based on converted amount, date, and description
            duplicate_query = Transaction.objects.filter(
                user=self.user,
                transaction_type=parsed_data['transaction_type'],
                amount=final_amount,
                date=parsed_data['date'],
                description__icontains=description[:20]  # Partial match on original description
            )
            
            existing_transaction = duplicate_query.first()
            if existing_transaction:
                logger.info(f"🔄 Duplicate found, linking to existing transaction {existing_transaction.id}")
                return existing_transaction
            
            # Parse date properly
            transaction_date = parsed_data['date']
            if isinstance(transaction_date, str):
                from datetime import datetime
                try:
                    transaction_date = datetime.strptime(transaction_date, '%Y-%m-%d').date()
                except ValueError:
                    from datetime import date
                    transaction_date = date.today()
                    logger.warning(f"⚠️ Invalid date format, using today: {transaction_date}")
            
            # Create new transaction with converted amount
            transaction = Transaction.objects.create(
                user=self.user,
                transaction_type=parsed_data['transaction_type'],
                amount=final_amount,
                description=final_description,
                date=transaction_date,
                expense_category=parsed_data.get('expense_category'),
                ai_confidence=parsed_data.get('ai_confidence', 0.5)
            )
            
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
    
    def get_sync_preview(self, bank_code: str = None, **sync_options) -> Dict[str, Any]:
        """
        Get preview of transactions that would be imported without actually creating them
        
        Args:
            bank_code: Specific bank to preview, or None for all enabled banks
            **sync_options: Additional sync parameters
            
        Returns:
            Preview data with transactions that would be imported
        """
        logger.info(f"🔍 Getting sync preview for user {self.user.email}")
        
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
            
            if not gmail_service.test_connection():
                return {
                    'success': False,
                    'error': 'Gmail connection failed',
                    'requires_gmail_auth': True
                }
            
            # Collect preview transactions from all banks
            all_preview_transactions = []
            
            for bank_config in bank_configs:
                preview_result = self._get_single_bank_preview(gmail_service, bank_config, sync_options)
                if preview_result.get('success'):
                    all_preview_transactions.extend(preview_result.get('transactions', []))
            
            return {
                'success': True,
                'transactions': all_preview_transactions,
                'total_count': len(all_preview_transactions)
            }
            
        except Exception as e:
            logger.error(f"Error getting sync preview: {str(e)}")
            return {
                'success': False,
                'error': f'Preview failed: {str(e)}'
            }
    
    def _get_single_bank_preview(self, gmail_service: GmailService, bank_config: UserBankConfig, sync_options: Dict[str, Any]) -> Dict[str, Any]:
        """Get preview for a single bank"""
        try:
            # Get bank sender emails
            sender_emails = BankEmailProcessor.get_bank_sender_emails(bank_config.bank_code, bank_config)
            if not sender_emails:
                return {'success': False, 'error': f'No sender emails for {bank_config.bank_code}'}
            
            # Determine sync date range
            since_datetime, until_datetime = self._calculate_sync_date_range(bank_config, sync_options)
            
            logger.info(f"📅 Sync date range: {since_datetime} to {until_datetime}")
            
            # Get emails from Gmail
            emails = gmail_service.get_bank_emails(sender_emails, since_datetime, until_datetime)
            logger.info(f"📧 Found {len(emails)} total emails from Gmail")
            
            # Filter for transaction emails
            transaction_emails = [
                email for email in emails
                if BankEmailProcessor.is_bank_transaction_email(email, bank_config.bank_code)
            ]
            logger.info(f"💳 Filtered to {len(transaction_emails)} transaction emails")
            
            # Check force refresh option
            force_refresh = sync_options.get('force_refresh', False)
            logger.info(f"🔄 Force refresh enabled: {force_refresh}")
            
            if force_refresh:
                # Clear existing records for this date range in force refresh mode
                since_datetime, until_datetime = self._calculate_sync_date_range(bank_config, sync_options)
                existing_count = BankEmailTransaction.objects.filter(
                    user=self.user,
                    bank_config=bank_config,
                    email_date__gte=since_datetime
                ).count()
                
                if until_datetime:
                    existing_count = BankEmailTransaction.objects.filter(
                        user=self.user,
                        bank_config=bank_config,
                        email_date__gte=since_datetime,
                        email_date__lte=until_datetime
                    ).count()
                
                logger.info(f"🔄 Force refresh mode: {existing_count} existing records in date range")
                
                # Include all emails for force refresh preview
                new_emails = transaction_emails
                logger.info(f"🔄 Force refresh: Using all {len(new_emails)} transaction emails for re-parsing")
            else:
                # Check for already processed emails
                existing_email_ids = set(
                    BankEmailTransaction.objects.filter(
                        user=self.user,
                        bank_config=bank_config
                    ).values_list('email_message_id', flat=True)
                )
                
                logger.info(f"📊 Total transaction emails: {len(transaction_emails)}, existing in DB: {len(existing_email_ids)}")
                
                new_emails = [
                    email for email in transaction_emails
                    if email.get('id') not in existing_email_ids
                ]
                
                logger.info(f"📊 New emails to process: {len(new_emails)}")
            
            logger.info(f"🔍 Found {len(new_emails)} new emails for preview")
            
            # Parse emails with AI (preview only)
            user_context = {
                'account_suffix': bank_config.account_suffix,
                'bank_code': bank_config.bank_code
            }
            
            logger.info(f"🤖 Starting AI parsing for {len(new_emails)} emails")
            try:
                parsed_transactions = self.parser.parse_multiple_emails(
                    new_emails, 
                    bank_config.bank_code, 
                    user_context
                )
                logger.info(f"✅ AI parsing completed: {len(parsed_transactions)} transactions parsed")
            except Exception as e:
                logger.error(f"❌ AI parsing failed: {str(e)}")
                return {'success': False, 'error': f'AI parsing failed: {str(e)}'}
            
            # Format for preview
            preview_transactions = []
            for i, parsed_data in enumerate(parsed_transactions):
                try:
                    preview_transactions.append({
                        'bank_code': bank_config.bank_code,
                        'email_id': parsed_data['email_id'],
                        'email_subject': parsed_data.get('email_subject', ''),
                        'email_date': parsed_data['email_date'].isoformat(),
                        'transaction_type': parsed_data['transaction_type'],
                        'amount': parsed_data['amount'],
                        'currency': parsed_data.get('currency', 'VND'),
                        'description': parsed_data['description'],
                        'date': parsed_data['date'].isoformat() if hasattr(parsed_data['date'], 'isoformat') else str(parsed_data['date']),
                        'expense_category': parsed_data.get('expense_category'),
                        'ai_confidence': parsed_data.get('ai_confidence', 0.5),
                        'is_new': True
                    })
                except Exception as e:
                    logger.error(f"❌ Error formatting transaction {i+1}: {str(e)}")
                    logger.error(f"   Raw data: {parsed_data}")
            
            logger.info(f"🎯 Preview result: {len(preview_transactions)} transactions formatted")
            
            return {
                'success': True,
                'transactions': preview_transactions
            }
            
        except Exception as e:
            logger.error(f"Error getting preview for {bank_config.bank_code}: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def import_selected_transactions(self, selected_transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Import only selected transactions from preview
        
        Args:
            selected_transactions: List of transaction data to import
            
        Returns:
            Import results
        """
        logger.info(f"📥 Importing {len(selected_transactions)} selected transactions")
        
        imported_count = 0
        skipped_count = 0
        import_details = []
        
        try:
            with db_transaction.atomic():
                for transaction_data in selected_transactions:
                    try:
                        # Get bank config
                        bank_config = UserBankConfig.objects.get(
                            user=self.user,
                            bank_code=transaction_data['bank_code']
                        )
                        
                        # Check if email already exists (for force refresh handling)
                        email_id = transaction_data['email_id']
                        existing_email_transaction = BankEmailTransaction.objects.filter(
                            user=self.user,
                            bank_config=bank_config,
                            email_message_id=email_id
                        ).first()
                        
                        if existing_email_transaction:
                            logger.info(f"🔄 Email {email_id[:20]}... already exists, updating with new data")
                            
                            # Delete old transaction if exists (for force refresh)
                            if existing_email_transaction.transaction_id:
                                old_transaction = existing_email_transaction.transaction_id
                                logger.info(f"🗑️ Deleting old transaction {old_transaction.id} for re-creation")
                                old_transaction.delete()
                            
                            # Update existing record with new parsed data
                            existing_email_transaction.email_date = transaction_data['email_date']
                            existing_email_transaction.email_subject = transaction_data.get('email_subject', '')
                            existing_email_transaction.transaction_type = transaction_data['transaction_type']
                            existing_email_transaction.amount = transaction_data['amount']
                            existing_email_transaction.description = transaction_data['description']
                            existing_email_transaction.date = transaction_data['date']
                            existing_email_transaction.expense_category = transaction_data.get('expense_category')
                            existing_email_transaction.ai_confidence = transaction_data.get('ai_confidence', 0.5)
                            existing_email_transaction.parsing_method = 'gemini'
                            existing_email_transaction.is_processed = False  # Mark as unprocessed for re-creation
                            existing_email_transaction.transaction_id = None  # Clear old transaction reference
                            existing_email_transaction.save()
                            
                            bank_email_transaction = existing_email_transaction
                        else:
                            # Create new BankEmailTransaction record
                            bank_email_transaction = BankEmailTransaction.objects.create(
                                user=self.user,
                                bank_config=bank_config,
                                email_message_id=transaction_data['email_id'],
                                email_date=transaction_data['email_date'],
                                email_subject=transaction_data.get('email_subject', ''),
                                transaction_type=transaction_data['transaction_type'],
                                amount=transaction_data['amount'],
                                description=transaction_data['description'],
                                date=transaction_data['date'],
                                expense_category=transaction_data.get('expense_category'),
                                ai_confidence=transaction_data.get('ai_confidence', 0.5),
                                parsing_method='gemini'
                            )
                        
                        # Create actual transaction with currency conversion
                        actual_transaction = self._create_actual_transaction(
                            bank_email_transaction, 
                            transaction_data
                        )
                        
                        if actual_transaction:
                            bank_email_transaction.transaction_id = actual_transaction
                            bank_email_transaction.is_processed = True
                            bank_email_transaction.save()
                            imported_count += 1
                            
                            logger.info(f"✅ Imported {transaction_data.get('description', 'N/A')[:30]}... → {actual_transaction.amount:,.0f} VND")
                            
                            import_details.append({
                                'email_id': transaction_data['email_id'],
                                'transaction_id': actual_transaction.id,
                                'status': 'imported',
                                'amount': float(actual_transaction.amount)
                            })
                        else:
                            skipped_count += 1
                            import_details.append({
                                'email_id': transaction_data['email_id'],
                                'status': 'skipped',
                                'reason': 'Failed to create transaction'
                            })
                            
                    except Exception as e:
                        skipped_count += 1
                        import_details.append({
                            'email_id': transaction_data.get('email_id', 'unknown'),
                            'status': 'error',
                            'reason': str(e)
                        })
                        logger.error(f"Error importing transaction: {str(e)}")
            
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'details': import_details
            }
            
        except Exception as e:
            logger.error(f"Error importing selected transactions: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

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