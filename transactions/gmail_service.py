"""
Gmail API Service for Bank Email Integration
Handles reading emails from supported banks
"""
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

class GmailService:
    """
    Gmail API service for reading bank emails
    Uses separate OAuth tokens from login (stored in UserGmailPermission)
    """
    
    def __init__(self, user_gmail_permission):
        """Initialize Gmail service with user's Gmail permission"""
        self.user_gmail_permission = user_gmail_permission
        self.user = user_gmail_permission.user
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize Gmail API service with user's OAuth tokens"""
        try:
            if not self.user_gmail_permission.has_gmail_permission:
                raise ValueError("User does not have Gmail permission")
            
            if self.user_gmail_permission.is_token_expired():
                # Try to refresh token
                self._refresh_token()
            
            # Create credentials from stored token
            token_data = self.user_gmail_permission.gmail_oauth_token
            if not token_data:
                raise ValueError("No Gmail OAuth token found")
            
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes', [])
            )
            
            # Build Gmail service
            self.service = build('gmail', 'v1', credentials=credentials)
            
            # Update last used timestamp
            self.user_gmail_permission.permission_last_used = timezone.now()
            self.user_gmail_permission.save()
            
            logger.info(f"Gmail service initialized for user {self.user.email}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gmail service for user {self.user.email}: {str(e)}")
            raise
    
    def _refresh_token(self):
        """Refresh expired Gmail token"""
        try:
            token_data = self.user_gmail_permission.gmail_oauth_token
            if not token_data or not token_data.get('refresh_token'):
                raise ValueError("No refresh token available")
            
            credentials = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes', [])
            )
            
            # Refresh the token
            from google.auth.transport.requests import Request
            credentials.refresh(Request())
            
            # Update stored token
            token_data['token'] = credentials.token
            self.user_gmail_permission.gmail_oauth_token = token_data
            self.user_gmail_permission.gmail_token_expires_at = credentials.expiry
            self.user_gmail_permission.save()
            
            logger.info(f"Gmail token refreshed for user {self.user.email}")
            
        except Exception as e:
            logger.error(f"Failed to refresh Gmail token for user {self.user.email}: {str(e)}")
            # Revoke permission if refresh fails
            self.user_gmail_permission.revoke_permission()
            raise
    
    def get_bank_emails(self, bank_sender_emails: List[str], since_date: datetime = None) -> List[Dict[str, Any]]:
        """
        Get emails from specific bank senders
        
        Args:
            bank_sender_emails: List of bank email addresses to search
            since_date: Only get emails after this date
            
        Returns:
            List of email data dictionaries
        """
        try:
            if not self.service:
                raise ValueError("Gmail service not initialized")
            
            # Build search query
            query_parts = []
            
            # Add sender filter
            if bank_sender_emails:
                sender_queries = [f"from:{email}" for email in bank_sender_emails]
                query_parts.append(f"({' OR '.join(sender_queries)})")
            
            # Add date filter
            if since_date:
                date_str = since_date.strftime('%Y/%m/%d')
                query_parts.append(f"after:{date_str}")
            
            # Only get emails from last 30 days max for performance
            default_since = datetime.now() - timedelta(days=30)
            if not since_date or since_date < default_since:
                default_date_str = default_since.strftime('%Y/%m/%d')
                query_parts.append(f"after:{default_date_str}")
            
            query = ' '.join(query_parts)
            
            logger.info(f"Searching Gmail with query: {query}")
            
            # Search for emails
            result = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=100  # Limit to prevent overload
            ).execute()
            
            messages = result.get('messages', [])
            
            # Get full email details
            emails = []
            for message in messages:
                try:
                    email_detail = self.get_email_detail(message['id'])
                    if email_detail:
                        emails.append(email_detail)
                except Exception as e:
                    logger.warning(f"Failed to get email detail for message {message['id']}: {str(e)}")
                    continue
            
            logger.info(f"Retrieved {len(emails)} bank emails for user {self.user.email}")
            return emails
            
        except HttpError as e:
            logger.error(f"Gmail API error for user {self.user.email}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting bank emails for user {self.user.email}: {str(e)}")
            raise
    
    def get_email_detail(self, message_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information for a specific email
        
        Args:
            message_id: Gmail message ID
            
        Returns:
            Email detail dictionary or None if error
        """
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            
            # Extract email headers
            headers = {}
            for header in message.get('payload', {}).get('headers', []):
                headers[header['name'].lower()] = header['value']
            
            # Extract email body
            body = self._extract_email_body(message.get('payload', {}))
            
            # Parse date
            email_date = self._parse_email_date(headers.get('date'))
            
            return {
                'id': message_id,
                'thread_id': message.get('threadId'),
                'subject': headers.get('subject', ''),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'date': email_date,
                'body': body,
                'snippet': message.get('snippet', ''),
                'headers': headers
            }
            
        except HttpError as e:
            logger.error(f"Gmail API error getting email detail {message_id}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting email detail {message_id}: {str(e)}")
            return None
    
    def _extract_email_body(self, payload: Dict[str, Any]) -> str:
        """Extract email body from Gmail payload"""
        try:
            body = ""
            
            # Handle multipart emails
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data')
                        if data:
                            import base64
                            body += base64.urlsafe_b64decode(data).decode('utf-8')
                            break
            else:
                # Single part email
                if payload.get('mimeType') == 'text/plain':
                    data = payload.get('body', {}).get('data')
                    if data:
                        import base64
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
            
            return body.strip()
            
        except Exception as e:
            logger.warning(f"Error extracting email body: {str(e)}")
            return ""
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to datetime"""
        try:
            if not date_str:
                return datetime.now()
            
            # Gmail date format: "Mon, 2 Oct 2023 10:30:00 +0700"
            from email.utils import parsedate_to_datetime
            return parsedate_to_datetime(date_str)
            
        except Exception as e:
            logger.warning(f"Error parsing email date {date_str}: {str(e)}")
            return datetime.now()
    
    def test_connection(self) -> bool:
        """Test Gmail API connection"""
        try:
            if not self.service:
                return False
            
            # Simple API call to test connection
            profile = self.service.users().getProfile(userId='me').execute()
            logger.info(f"Gmail connection test successful for {profile.get('emailAddress')}")
            return True
            
        except Exception as e:
            logger.error(f"Gmail connection test failed for user {self.user.email}: {str(e)}")
            return False


class BankEmailProcessor:
    """
    Process bank emails for specific banks
    Knows which email patterns to look for each bank
    """
    
    # TPBank email configuration
    TPBANK_CONFIG = {
        'sender_emails': [
            'tpbank@tpb.com.vn',
            'noreply@tpbank.com.vn',
            'notification@tpb.com.vn'
        ],
        'subject_keywords': [
            'Thông báo giao dịch',
            'Transaction notification', 
            'Biến động số dư',
            'Balance change'
        ]
    }
    
    # Bank configurations
    BANK_CONFIGS = {
        'tpbank': TPBANK_CONFIG,
        # Add more banks in Phase 2
    }
    
    @classmethod
    def get_bank_sender_emails(cls, bank_code: str) -> List[str]:
        """Get sender email patterns for a specific bank"""
        config = cls.BANK_CONFIGS.get(bank_code, {})
        return config.get('sender_emails', [])
    
    @classmethod
    def is_bank_transaction_email(cls, email: Dict[str, Any], bank_code: str) -> bool:
        """Check if email is a transaction notification from the bank"""
        config = cls.BANK_CONFIGS.get(bank_code, {})
        subject_keywords = config.get('subject_keywords', [])
        
        subject = email.get('subject', '').lower()
        
        # Check if subject contains transaction keywords
        for keyword in subject_keywords:
            if keyword.lower() in subject:
                return True
        
        return False 