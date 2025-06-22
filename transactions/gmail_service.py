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
            
            # Handle timezone for token expiry
            if credentials.expiry:
                if credentials.expiry.tzinfo is None:
                    self.user_gmail_permission.gmail_token_expires_at = timezone.make_aware(credentials.expiry)
                else:
                    self.user_gmail_permission.gmail_token_expires_at = credentials.expiry
            else:
                self.user_gmail_permission.gmail_token_expires_at = None
                
            self.user_gmail_permission.save()
            
            logger.info(f"Gmail token refreshed for user {self.user.email}")
            
        except Exception as e:
            logger.error(f"Failed to refresh Gmail token for user {self.user.email}: {str(e)}")
            # Revoke permission if refresh fails
            self.user_gmail_permission.revoke_permission()
            raise
    
    def get_bank_emails(self, sender_emails: List[str], since_datetime: datetime = None, until_datetime: datetime = None) -> List[Dict[str, Any]]:
        """
        Get bank emails from Gmail with flexible date filtering
        
        Args:
            sender_emails: List of sender email patterns to filter
            since_datetime: Start date for email filtering
            until_datetime: End date for email filtering (optional)
            
        Returns:
            List of email dictionaries
        """
        try:
            if not self.service:
                return []
            
            # Build Gmail search query
            query_parts = []
            
            # Add sender filters
            if sender_emails:
                sender_query = ' OR '.join([f'from:{email}' for email in sender_emails])
                query_parts.append(f'({sender_query})')
            
            # Add date filters
            if since_datetime:
                since_date_str = since_datetime.strftime('%Y/%m/%d')
                query_parts.append(f'after:{since_date_str}')
            
            if until_datetime:
                until_date_str = until_datetime.strftime('%Y/%m/%d')
                query_parts.append(f'before:{until_date_str}')
            
            # Build final query
            query = ' '.join(query_parts) if query_parts else 'in:inbox'
            
            logger.info(f"Gmail search query: {query}")
            
            # Search for messages
            results = self.service.users().messages().list(
                userId='me',
                q=query,
                maxResults=500  # Increased limit for batch processing
            ).execute()
            
            messages = results.get('messages', [])
            logger.info(f"Found {len(messages)} messages matching criteria")
            
            # Get detailed message information
            emails = []
            for message in messages:
                try:
                    msg_detail = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    email_data = self._parse_email_message(msg_detail)
                    if email_data:
                        emails.append(email_data)
                        
                except Exception as e:
                    logger.warning(f"Error getting message details for {message['id']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully parsed {len(emails)} emails")
            return emails
            
        except Exception as e:
            logger.error(f"Error getting bank emails: {str(e)}")
            return []
    
    def _parse_email_message(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse Gmail message to extract relevant information
        
        Args:
            message: Gmail message object
            
        Returns:
            Parsed email data dictionary
        """
        try:
            # Extract headers
            headers = {}
            for header in message.get('payload', {}).get('headers', []):
                headers[header['name'].lower()] = header['value']
            
            # Extract email body
            body = self._extract_email_body(message.get('payload', {}))
            
            # Parse date with timezone awareness
            email_date = self._parse_email_date(headers.get('date'))
            
            return {
                'id': message['id'],
                'thread_id': message.get('threadId'),
                'subject': headers.get('subject', ''),
                'from': headers.get('from', ''),
                'to': headers.get('to', ''),
                'date': email_date,
                'body': body,
                'headers': headers,
                'message_id': headers.get('message-id', ''),
                'internal_date': int(message.get('internalDate', 0))
            }
            
        except Exception as e:
            logger.error(f"Error parsing email message: {str(e)}")
            return None
    
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
            logger.warning(f"📧 DEBUG: Extracting body from payload mimeType: {payload.get('mimeType')}")
            logger.warning(f"📧 DEBUG: Has parts: {'parts' in payload}")
            
            # Handle multipart emails
            if 'parts' in payload:
                logger.warning(f"📧 DEBUG: Processing {len(payload['parts'])} parts")
                for i, part in enumerate(payload['parts']):
                    mime_type = part.get('mimeType')
                    has_data = bool(part.get('body', {}).get('data'))
                    logger.warning(f"📧 DEBUG: Part {i}: mimeType={mime_type}, has_data={has_data}")
                    
                    # Try text/plain first, then text/html
                    if mime_type in ['text/plain', 'text/html']:
                        data = part.get('body', {}).get('data')
                        if data:
                            import base64
                            try:
                                decoded = base64.urlsafe_b64decode(data).decode('utf-8')
                                body += decoded
                                logger.warning(f"📧 DEBUG: Successfully decoded part {i} ({mime_type}): {decoded[:200]}...")
                                if mime_type == 'text/plain':
                                    break  # Prefer plain text
                            except Exception as e:
                                logger.warning(f"📧 DEBUG: Failed to decode part {i}: {str(e)}")
            else:
                # Single part email
                mime_type = payload.get('mimeType')
                logger.warning(f"📧 DEBUG: Single part email, mimeType: {mime_type}")
                
                if mime_type in ['text/plain', 'text/html']:
                    data = payload.get('body', {}).get('data')
                    if data:
                        import base64
                        try:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            logger.warning(f"📧 DEBUG: Successfully decoded single part: {body[:200]}...")
                        except Exception as e:
                            logger.warning(f"📧 DEBUG: Failed to decode single part: {str(e)}")
            
            logger.warning(f"📧 DEBUG: Final body length: {len(body)}")
            
            # Strip HTML tags to get plain text for AI parsing
            if body and (body.strip().startswith('<!DOCTYPE') or '<html' in body.lower()):
                logger.warning(f"📧 DEBUG: Detected HTML content, stripping tags...")
                import re
                
                # More comprehensive HTML cleaning
                clean_body = body
                
                # Remove CSS styles and scripts
                clean_body = re.sub(r'<style[^>]*>.*?</style>', ' ', clean_body, flags=re.DOTALL | re.IGNORECASE)
                clean_body = re.sub(r'<script[^>]*>.*?</script>', ' ', clean_body, flags=re.DOTALL | re.IGNORECASE)
                
                # Remove HTML tags
                clean_body = re.sub(r'<[^>]+>', ' ', clean_body)
                
                # Remove CSS-like patterns that survived tag removal
                clean_body = re.sub(r'\{[^}]*\}', ' ', clean_body)
                clean_body = re.sub(r'#[\w-]+', ' ', clean_body)
                clean_body = re.sub(r'\.[\w-]+', ' ', clean_body)
                
                # Clean up common HTML entities
                clean_body = clean_body.replace('&nbsp;', ' ')
                clean_body = clean_body.replace('&amp;', '&')
                clean_body = clean_body.replace('&lt;', '<')
                clean_body = clean_body.replace('&gt;', '>')
                
                # Clean up whitespace and formatting
                clean_body = re.sub(r'\s+', ' ', clean_body).strip()
                
                # Remove lines that are just CSS or formatting remnants
                lines = [line.strip() for line in clean_body.split('\n') if line.strip()]
                filtered_lines = []
                for line in lines:
                    # Skip lines that look like CSS or formatting
                    if not ((':' in line and ';' in line) or 
                           line.startswith('#') or 
                           line.startswith('.') or
                           'font-' in line or
                           'color:' in line or
                           'text-decoration' in line):
                        filtered_lines.append(line)
                
                clean_body = ' '.join(filtered_lines)
                
                logger.warning(f"📧 DEBUG: HTML stripped, new length: {len(clean_body)}")
                logger.warning(f"📧 DEBUG: Clean text content (first 500 chars): {clean_body[:500]}...")
                return clean_body
            
            return body.strip()
            
        except Exception as e:
            logger.warning(f"Error extracting email body: {str(e)}")
            return ""
    
    def _parse_email_date(self, date_str: str) -> datetime:
        """Parse email date string to timezone-aware datetime"""
        try:
            if not date_str:
                return timezone.now()
            
            # Gmail date format: "Mon, 2 Oct 2023 10:30:00 +0700"
            from email.utils import parsedate_to_datetime
            parsed_date = parsedate_to_datetime(date_str)
            
            # Ensure timezone awareness
            if parsed_date.tzinfo is None:
                # If no timezone info, assume UTC
                parsed_date = timezone.make_aware(parsed_date, timezone.utc)
            
            return parsed_date
            
        except Exception as e:
            logger.warning(f"Error parsing email date {date_str}: {str(e)}")
            return timezone.now()
    
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
    def get_bank_sender_emails(cls, bank_code: str, user_bank_config=None) -> List[str]:
        """Get sender email patterns for a specific bank (predefined or custom)"""
        # For custom banks, use the user-configured sender pattern
        if user_bank_config and user_bank_config.is_custom_bank and user_bank_config.sender_email_pattern:
            return [user_bank_config.sender_email_pattern]
        
        # For predefined banks, use default configuration
        config = cls.BANK_CONFIGS.get(bank_code, {})
        return config.get('sender_emails', [])
    
    @classmethod
    def is_bank_transaction_email(cls, email: Dict[str, Any], bank_code: str) -> bool:
        """Check if email is a transaction notification from the bank"""
        # For custom banks, we accept all emails from the configured sender
        if bank_code.startswith('custom_'):
            # Assume all emails from custom bank senders are transaction emails
            return True
        
        # For predefined banks, check subject keywords
        config = cls.BANK_CONFIGS.get(bank_code, {})
        subject_keywords = config.get('subject_keywords', [])
        
        subject = email.get('subject', '').lower()
        
        # Check if subject contains transaction keywords
        for keyword in subject_keywords:
            if keyword.lower() in subject:
                return True
        
        # If no specific keywords configured, accept all emails (for compatibility)
        if not subject_keywords:
            return True
        
        return False 