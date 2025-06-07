import re
from datetime import datetime, timedelta, date
from django.utils.translation import gettext as _
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class DateParser:
    """
    Parse dates from Vietnamese and English natural language expressions
    """
    
    def __init__(self, language='vi'):
        self.language = language
        self.today = date.today()
        
    def parse_date_from_message(self, message: str) -> date:
        """Parse date from Vietnamese/English message"""
        if not message:
            return self.today
            
        message_lower = message.lower().strip()
        
        try:
            # Check for day before yesterday FIRST (more specific)
            if self._is_day_before_yesterday(message_lower):
                return self.today - timedelta(days=2)
            
            # Check for today variations
            if self._is_today(message_lower):
                return self.today
            
            # Check for yesterday variations  
            if self._is_yesterday(message_lower):
                return self.today - timedelta(days=1)
            
            # Check for specific weekdays
            weekday_date = self._parse_weekday(message_lower)
            if weekday_date:
                return weekday_date
            
            # Check for relative time expressions
            relative_date = self._parse_relative_expressions(message_lower)
            if relative_date:
                return relative_date
            
            # Check for specific date patterns (dd/mm, dd-mm, dd.mm)
            specific_date = self._parse_specific_date(message_lower)
            if specific_date:
                return specific_date
            
        except Exception as e:
            logger.error(f"Error parsing date from '{message}': {e}")
        
        # Default to today
        return self.today
    
    def _is_today(self, message: str) -> bool:
        """Check if message refers to today"""
        today_patterns = {
            'vi': ['hôm nay', 'bữa nay', 'ngày hôm nay', 'h nay', 'hnay'],
            'en': ['today', 'this day', 'now']
        }
        
        patterns = today_patterns.get(self.language, today_patterns['vi'])
        return any(pattern in message for pattern in patterns)
    
    def _is_yesterday(self, message: str) -> bool:
        """Check if message refers to yesterday"""
        yesterday_patterns = {
            'vi': ['hôm qua', 'qua', 'ngày hôm qua', 'h qua', 'hqua'],
            'en': ['yesterday', 'last day', 'yest']
        }
        
        patterns = yesterday_patterns.get(self.language, yesterday_patterns['vi'])
        return any(pattern in message for pattern in patterns)
    
    def _is_day_before_yesterday(self, message: str) -> bool:
        """Check if message refers to day before yesterday"""
        day_before_patterns = {
            'vi': ['hôm kia', 'ngày kia'],  # Remove 'kia' alone to avoid conflicts
            'en': ['day before yesterday', 'before yesterday']
        }
        
        patterns = day_before_patterns.get(self.language, day_before_patterns['vi'])
        return any(pattern in message for pattern in patterns)
    
    def _parse_weekday(self, message: str) -> Optional[date]:
        """Parse weekday references"""
        weekdays = {
            'vi': {
                'thứ hai': 0, 'thứ 2': 0, 't2': 0, 'thu 2': 0,
                'thứ ba': 1, 'thứ 3': 1, 't3': 1, 'thu 3': 1,
                'thứ tư': 2, 'thứ 4': 2, 't4': 2, 'thu 4': 2,
                'thứ năm': 3, 'thứ 5': 3, 't5': 3, 'thu 5': 3,
                'thứ sáu': 4, 'thứ 6': 4, 't6': 4, 'thu 6': 4,
                'thứ bảy': 5, 'thứ 7': 5, 't7': 5, 'thu 7': 5,
                'chủ nhật': 6, 'cn': 6, 'chu nhat': 6
            },
            'en': {
                'monday': 0, 'mon': 0,
                'tuesday': 1, 'tue': 1, 'tues': 1,
                'wednesday': 2, 'wed': 2,
                'thursday': 3, 'thu': 3, 'thurs': 3,
                'friday': 4, 'fri': 4,
                'saturday': 5, 'sat': 5,
                'sunday': 6, 'sun': 6
            }
        }
        
        day_mapping = weekdays.get(self.language, weekdays['vi'])
        
        # Check for weekday with "last" or "tuần trước"
        for day_name, day_num in day_mapping.items():
            if day_name in message:
                # Check if it's referring to last week
                if any(phrase in message for phrase in ['tuần trước', 'last week', 'last', 'trước']):
                    return self._get_last_weekday(day_num, weeks_back=1)
                else:
                    return self._get_last_weekday(day_num)
        
        return None
    
    def _parse_relative_expressions(self, message: str) -> Optional[date]:
        """Parse relative time expressions"""
        
        # Parse "X days ago" / "X ngày trước"
        if self.language == 'vi':
            # Pattern for "X ngày trước"
            match = re.search(r'(\d+)\s*ngày\s*trước', message)
            if match:
                days_back = int(match.group(1))
                return self.today - timedelta(days=days_back)
            
            # Pattern for "X tuần trước"
            match = re.search(r'(\d+)\s*tuần\s*trước', message)
            if match:
                weeks_back = int(match.group(1))
                return self.today - timedelta(weeks=weeks_back)
        else:
            # Pattern for "X days ago"
            match = re.search(r'(\d+)\s*days?\s*ago', message)
            if match:
                days_back = int(match.group(1))
                return self.today - timedelta(days=days_back)
            
            # Pattern for "X weeks ago"
            match = re.search(r'(\d+)\s*weeks?\s*ago', message)
            if match:
                weeks_back = int(match.group(1))
                return self.today - timedelta(weeks=weeks_back)
        
        return None
    
    def _parse_specific_date(self, message: str) -> Optional[date]:
        """Parse specific date patterns like dd/mm, dd-mm, dd.mm"""
        
        # Try various date formats
        date_patterns = [
            r'(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})',  # dd/mm/yyyy
            r'(\d{1,2})[/\-.](\d{1,2})',  # dd/mm (current year)
            r'ngày\s*(\d{1,2})[/\-.](\d{1,2})',  # ngày dd/mm
            r'on\s*(\d{1,2})[/\-.](\d{1,2})',  # on dd/mm
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                try:
                    if len(match.groups()) == 3:
                        # Full date with year
                        day, month, year = int(match.group(1)), int(match.group(2)), int(match.group(3))
                    else:
                        # Date without year, assume current year
                        day, month = int(match.group(1)), int(match.group(2))
                        year = self.today.year
                    
                    # Validate date
                    if 1 <= month <= 12 and 1 <= day <= 31:
                        target_date = date(year, month, day)
                        
                        # If date is in future (and we assumed current year), use previous year
                        if target_date > self.today and len(match.groups()) == 2:
                            target_date = date(year - 1, month, day)
                        
                        return target_date
                        
                except ValueError:
                    # Invalid date, continue to next pattern
                    continue
        
        return None
    
    def _get_last_weekday(self, target_weekday: int, weeks_back: int = 0) -> date:
        """Get the most recent occurrence of a weekday"""
        current_weekday = self.today.weekday()
        
        if weeks_back == 0:
            # Get most recent occurrence
            days_back = (current_weekday - target_weekday) % 7
            if days_back == 0:  # Same day, get last week's occurrence
                days_back = 7
        else:
            # Get specific week back
            days_back = (current_weekday - target_weekday) + (7 * weeks_back)
            if current_weekday < target_weekday:
                days_back += 7
        
        return self.today - timedelta(days=days_back)
    
    def format_parsed_date(self, parsed_date: date) -> str:
        """Format parsed date for display"""
        if self.language == 'vi':
            if parsed_date == self.today:
                return "hôm nay"
            elif parsed_date == self.today - timedelta(days=1):
                return "hôm qua"
            elif parsed_date == self.today - timedelta(days=2):
                return "hôm kia"
            else:
                return parsed_date.strftime("%d/%m/%Y")
        else:
            if parsed_date == self.today:
                return "today"
            elif parsed_date == self.today - timedelta(days=1):
                return "yesterday"
            elif parsed_date == self.today - timedelta(days=2):
                return "day before yesterday"
            else:
                return parsed_date.strftime("%m/%d/%Y")
    
    def get_relative_description(self, parsed_date: date) -> str:
        """Get a relative description of the parsed date"""
        days_diff = (self.today - parsed_date).days
        
        if self.language == 'vi':
            if days_diff == 0:
                return "hôm nay"
            elif days_diff == 1:
                return "hôm qua"
            elif days_diff == 2:
                return "hôm kia"
            elif days_diff < 7:
                return f"{days_diff} ngày trước"
            elif days_diff < 30:
                weeks = days_diff // 7
                return f"{weeks} tuần trước"
            else:
                return parsed_date.strftime("%d/%m/%Y")
        else:
            if days_diff == 0:
                return "today"
            elif days_diff == 1:
                return "yesterday"
            elif days_diff == 2:
                return "day before yesterday"
            elif days_diff < 7:
                return f"{days_diff} days ago"
            elif days_diff < 30:
                weeks = days_diff // 7
                return f"{weeks} weeks ago"
            else:
                return parsed_date.strftime("%m/%d/%Y") 