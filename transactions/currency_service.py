"""
Currency Conversion Service
Handles USD to VND conversion using exchangerate-api.com
"""
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger(__name__)

class CurrencyService:
    """
    Service for currency conversion using exchangerate-api.com
    Supports USD to VND conversion with caching
    """
    
    def __init__(self):
        self.api_key = getattr(settings, 'EXCHANGE_RATE_API_KEY', '6ecc6c7b04132c0c111d5a40')
        self.base_url = 'https://v6.exchangerate-api.com/v6'
        self.cache_timeout = 3600  # Cache for 1 hour
    
    def get_usd_to_vnd_rate(self) -> Optional[float]:
        """
        Get current USD to VND exchange rate
        Uses caching to avoid excessive API calls
        
        Returns:
            Exchange rate as float or None if failed
        """
        cache_key = 'usd_vnd_exchange_rate'
        
        # Try to get from cache first
        cached_rate = cache.get(cache_key)
        if cached_rate:
            logger.info(f"Using cached USD to VND rate: {cached_rate}")
            return cached_rate
        
        try:
            # Fetch from API
            url = f"{self.base_url}/{self.api_key}/latest/USD"
            
            logger.info(f"Fetching exchange rate from: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('result') != 'success':
                logger.error(f"Exchange rate API error: {data.get('error-type', 'Unknown error')}")
                return None
            
            # Get VND rate
            conversion_rates = data.get('conversion_rates', {})
            vnd_rate = conversion_rates.get('VND')
            
            if not vnd_rate:
                logger.error("VND rate not found in API response")
                return None
            
            # Cache the rate
            cache.set(cache_key, vnd_rate, self.cache_timeout)
            
            logger.info(f"Successfully fetched USD to VND rate: {vnd_rate}")
            return float(vnd_rate)
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching exchange rate: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error fetching exchange rate: {str(e)}")
            return None
    
    def convert_usd_to_vnd(self, usd_amount: float) -> Optional[float]:
        """
        Convert USD amount to VND
        
        Args:
            usd_amount: Amount in USD
            
        Returns:
            Amount in VND or None if conversion failed
        """
        if usd_amount <= 0:
            return usd_amount
        
        exchange_rate = self.get_usd_to_vnd_rate()
        if not exchange_rate:
            logger.warning(f"Could not get exchange rate, using fallback rate")
            # Fallback rate (approximate)
            exchange_rate = 24000.0
        
        vnd_amount = usd_amount * exchange_rate
        
        logger.info(f"Converted ${usd_amount} USD to {vnd_amount:,.0f} VND (rate: {exchange_rate})")
        return round(vnd_amount, 0)  # Round to nearest VND
    
    def detect_currency_and_convert(self, amount: float, description: str = "") -> Dict[str, Any]:
        """
        Detect currency from transaction description and convert if needed
        
        Args:
            amount: Transaction amount
            description: Transaction description to detect currency
            
        Returns:
            Dict with converted amount and currency info
        """
        # Currency detection patterns
        usd_patterns = ['USD', '$', 'dollar', 'DOLLAR', 'usd']
        
        original_currency = 'VND'  # Default assumption
        converted_amount = amount
        exchange_rate = None
        
        # Check if transaction contains USD indicators
        description_upper = description.upper()
        if any(pattern in description_upper for pattern in usd_patterns):
            original_currency = 'USD'
            
            # Convert to VND
            vnd_amount = self.convert_usd_to_vnd(amount)
            if vnd_amount:
                converted_amount = vnd_amount
                exchange_rate = self.get_usd_to_vnd_rate()
                
                logger.info(f"Detected USD transaction: ${amount} -> {converted_amount:,.0f} VND")
            else:
                logger.warning(f"Failed to convert USD amount: ${amount}")
        
        return {
            'original_amount': amount,
            'original_currency': original_currency,
            'converted_amount': converted_amount,
            'final_currency': 'VND',
            'exchange_rate': exchange_rate,
            'conversion_applied': original_currency != 'VND'
        }
    
    def get_rate_info(self) -> Dict[str, Any]:
        """
        Get current exchange rate information for display
        
        Returns:
            Dict with rate info and last update time
        """
        cache_key = 'usd_vnd_exchange_rate'
        rate = cache.get(cache_key)
        
        if not rate:
            rate = self.get_usd_to_vnd_rate()
        
        return {
            'usd_to_vnd_rate': rate,
            'last_updated': datetime.now().isoformat(),
            'source': 'exchangerate-api.com',
            'cache_timeout_minutes': self.cache_timeout // 60
        } 