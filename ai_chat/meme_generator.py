"""
AI Meme Generator for Expense Tracker
Analyzes weekly spending patterns and generates humorous memes
"""

from datetime import datetime, timedelta
from django.db.models import Sum
from django.utils.translation import gettext as _
from django.core.cache import cache
import random
import hashlib
from typing import Dict, List, Any
from transactions.models import Transaction

class MemeGenerator:
    def __init__(self, language='vi'):
        self.language = language
        
        # Meme templates with their trigger conditions
        self.meme_templates = {
            'drake_pointing': {
                'name': 'Drake Pointing',
                'image': 'drake_pointing.jpg',
                'format': 'comparison',
                'personality_weights': {
                    'coffee_addict': 3,
                    'foodie_explorer': 2,
                    'saving_master': 1,
                    'balanced_spender': 2
                }
            },
            'success_kid': {
                'name': 'Success Kid',
                'image': 'success_kid.jpg', 
                'format': 'achievement',
                'personality_weights': {
                    'coffee_addict': 1,
                    'foodie_explorer': 1,
                    'saving_master': 3,
                    'balanced_spender': 2
                }
            },
            'this_is_fine': {
                'name': 'This is Fine',
                'image': 'this_is_fine.jpg',
                'format': 'ironic',
                'personality_weights': {
                    'coffee_addict': 3,
                    'foodie_explorer': 3,
                    'saving_master': 0,
                    'balanced_spender': 2
                }
            },
            'expanding_brain': {
                'name': 'Expanding Brain',
                'image': 'expanding_brain.jpg',
                'format': 'escalation',
                'personality_weights': {
                    'coffee_addict': 2,
                    'foodie_explorer': 2,
                    'saving_master': 2,
                    'balanced_spender': 3
                }
            }
        }
        
        # Personality-specific meme texts
        self.meme_texts = {
            'vi': {
                'coffee_addict': {
                    'drake_pointing': {
                        'top': 'Tôi sẽ tiết kiệm tuần này',
                        'bottom': 'Đã order coffee 15 ly'
                    },
                    'success_kid': 'Chỉ uống 10 ly coffee tuần này thay vì 15!',
                    'this_is_fine': 'Chi 375k cho coffee tuần này. This is fine.',
                    'expanding_brain': [
                        'Coffee 25k/ly',
                        'Coffee premium 35k/ly', 
                        'Coffee + bánh 50k',
                        'Coffee shop hopping 400k/tuần'
                    ]
                },
                'foodie_explorer': {
                    'drake_pointing': {
                        'top': 'Nấu ăn tại nhà',
                        'bottom': 'Khám phá quán mới mỗi ngày'
                    },
                    'success_kid': 'Tìm được quán ngon mà không đắt!',
                    'this_is_fine': 'Chi 1.2M cho ăn uống tuần này. Đó là đầu tư!',
                    'expanding_brain': [
                        'Ăn cơm bình dân',
                        'Thử món mới',
                        'Check-in quán trendy',
                        'Food tour cuối tuần'
                    ]
                },
                'saving_master': {
                    'drake_pointing': {
                        'top': 'Chi tiêu không cần thiết',
                        'bottom': 'Tiết kiệm mọi đồng xu'
                    },
                    'success_kid': 'Tiết kiệm được 800k tuần này!',
                    'this_is_fine': 'Tiết kiệm 50% thu nhập. Perfectly normal.',
                    'expanding_brain': [
                        'Tiết kiệm 100k/tuần',
                        'Tiết kiệm 300k/tuần',
                        'Tiết kiệm 500k/tuần',
                        'Tiết kiệm = life goal'
                    ]
                },
                'balanced_spender': {
                    'drake_pointing': {
                        'top': 'Chi tiêu bừa bãi',
                        'bottom': 'Cân bằng thu chi hợp lý'
                    },
                    'success_kid': 'Tháng này cân bằng được thu chi!',
                    'this_is_fine': 'Chi tiêu vừa phải, tiết kiệm vừa phải. Balanced.',
                    'expanding_brain': [
                        'Lập kế hoạch chi tiêu',
                        'Theo dõi từng giao dịch',
                        'Phân bố ngân sách',
                        'Zen master của tài chính'
                    ]
                }
            },
            'en': {
                'coffee_addict': {
                    'drake_pointing': {
                        'top': 'I will save money this week',
                        'bottom': 'Already ordered 15 coffees'
                    },
                    'success_kid': 'Only had 10 coffees this week instead of 15!',
                    'this_is_fine': 'Spent 375k on coffee this week. This is fine.',
                    'expanding_brain': [
                        'Coffee 25k/cup',
                        'Premium coffee 35k/cup',
                        'Coffee + pastry 50k',
                        'Coffee shop hopping 400k/week'
                    ]
                },
                'foodie_explorer': {
                    'drake_pointing': {
                        'top': 'Cook at home',
                        'bottom': 'Explore new restaurants daily'
                    },
                    'success_kid': 'Found a delicious place that\'s not expensive!',
                    'this_is_fine': 'Spent 1.2M on food this week. It\'s an investment!',
                    'expanding_brain': [
                        'Local street food',
                        'Try new dishes',
                        'Check-in trendy places',
                        'Weekend food tours'
                    ]
                },
                'saving_master': {
                    'drake_pointing': {
                        'top': 'Unnecessary spending',
                        'bottom': 'Save every penny'
                    },
                    'success_kid': 'Saved 800k this week!',
                    'this_is_fine': 'Saved 50% of income. Perfectly normal.',
                    'expanding_brain': [
                        'Save 100k/week',
                        'Save 300k/week', 
                        'Save 500k/week',
                        'Saving = life goal'
                    ]
                },
                'balanced_spender': {
                    'drake_pointing': {
                        'top': 'Random spending',
                        'bottom': 'Balanced income & expenses'
                    },
                    'success_kid': 'Balanced income and expenses this month!',
                    'this_is_fine': 'Moderate spending, moderate saving. Balanced.',
                    'expanding_brain': [
                        'Plan expenses',
                        'Track every transaction',
                        'Budget allocation',
                        'Financial zen master'
                    ]
                }
            }
        }

    def generate_weekly_meme(self, user_transactions=None) -> Dict[str, Any]:
        """Generate a weekly meme based on user's spending patterns"""
        
        # Create cache key based on date and language
        today = datetime.now().date()
        cache_key = f"weekly_meme_{today}_{self.language}"
        
        # Check cache first (cache for 1 hour to allow some variation)
        if not user_transactions:  # Only cache when using real data
            cached_meme = cache.get(cache_key)
            if cached_meme:
                return cached_meme
        
        # Get weekly analysis
        analysis = self._analyze_weekly_spending(user_transactions)
        
        # Determine personality
        personality = self._determine_personality(analysis)
        
        # Choose meme template
        template = self._choose_meme_template(personality)
        
        # Generate meme text
        meme_text = self._generate_meme_text(personality, template, analysis)
        
        # Create meme data
        meme_data = {
            'template': template,
            'personality': personality,
            'analysis': analysis,
            'text': meme_text,
            'image_url': f'/static/images/meme_templates/{self.meme_templates[template]["image"]}',
            'shareable_text': self._create_shareable_text(personality, analysis)
        }
        
        # Cache the result for 1 hour
        if not user_transactions:
            cache.set(cache_key, meme_data, 3600)
        
        return meme_data

    def _analyze_weekly_spending(self, user_transactions=None) -> Dict[str, Any]:
        """Analyze spending patterns for the past week"""
        
        # Get date range for past week
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        # Query transactions for the past week
        if user_transactions is None:
            transactions = Transaction.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            )
        else:
            transactions = user_transactions
        
        # Calculate totals by type
        expense_total = abs(transactions.filter(
            transaction_type='expense'
        ).aggregate(total=Sum('amount'))['total'] or 0)
        
        saving_total = transactions.filter(
            transaction_type='saving'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        investment_total = transactions.filter(
            transaction_type='investment'
        ).aggregate(total=Sum('amount'))['total'] or 0
        
        # Calculate category breakdowns for expenses
        category_totals = {}
        expense_transactions = transactions.filter(transaction_type='expense')
        
        for transaction in expense_transactions:
            category = transaction.expense_category or 'other'
            if category not in category_totals:
                category_totals[category] = 0
            category_totals[category] += abs(transaction.amount)
        
        # Find dominant category
        dominant_category = max(category_totals.items(), key=lambda x: x[1]) if category_totals else ('other', 0)
        
        # Calculate transaction frequency
        transaction_count = transactions.count()
        
        return {
            'expense_total': expense_total,
            'saving_total': saving_total,
            'investment_total': investment_total,
            'net_total': saving_total + investment_total - expense_total,
            'category_totals': category_totals,
            'dominant_category': dominant_category[0],
            'dominant_category_amount': dominant_category[1],
            'transaction_count': transaction_count,
            'start_date': start_date,
            'end_date': end_date
        }

    def _determine_personality(self, analysis: Dict[str, Any]) -> str:
        """Determine user's spending personality based on analysis"""
        
        expense_total = analysis['expense_total']
        saving_total = analysis['saving_total']
        category_totals = analysis['category_totals']
        dominant_category = analysis['dominant_category']
        
        # Coffee Addict: >300k coffee/week
        coffee_amount = category_totals.get('coffee', 0)
        if coffee_amount > 300000:
            return 'coffee_addict'
        
        # Foodie Explorer: >1M food/week or food is dominant category with >500k
        food_amount = category_totals.get('food', 0)
        if food_amount > 1000000 or (dominant_category == 'food' and food_amount > 500000):
            return 'foodie_explorer'
        
        # Saving Master: high savings ratio (saving > 50% of total financial activity)
        total_financial_activity = expense_total + saving_total
        if total_financial_activity > 0 and (saving_total / total_financial_activity) > 0.5:
            return 'saving_master'
        
        # Default: Balanced Spender
        return 'balanced_spender'

    def _choose_meme_template(self, personality: str) -> str:
        """Choose appropriate meme template based on personality"""
        
        # Get weighted choices for this personality
        template_weights = []
        for template, data in self.meme_templates.items():
            weight = data['personality_weights'].get(personality, 1)
            template_weights.extend([template] * weight)
        
        # Randomly choose with weights
        return random.choice(template_weights) if template_weights else 'drake_pointing'

    def _generate_meme_text(self, personality: str, template: str, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate meme text based on personality and template"""
        
        texts = self.meme_texts.get(self.language, self.meme_texts['vi'])
        personality_texts = texts.get(personality, texts['balanced_spender'])
        
        if template in personality_texts:
            base_text = personality_texts[template]
            
            # Customize text with actual data
            if isinstance(base_text, dict):  # Drake pointing format
                return base_text
            elif isinstance(base_text, list):  # Expanding brain format
                return {'levels': base_text}
            else:  # Single text format
                return {'text': base_text}
        
        # Fallback
        return {'text': 'Chi tiêu của bạn tuần này thật thú vị! 🤔'}

    def _create_shareable_text(self, personality: str, analysis: Dict[str, Any]) -> str:
        """Create shareable text for social media"""
        
        if self.language == 'vi':
            personality_labels = {
                'coffee_addict': f"☕ Coffee Addict - Chi {analysis['category_totals'].get('coffee', 0):,}₫ cho coffee tuần này!",
                'foodie_explorer': f"🍜 Foodie Explorer - Khám phá ẩm thực với {analysis['category_totals'].get('food', 0):,}₫!",
                'saving_master': f"💰 Saving Master - Tiết kiệm {analysis['saving_total']:,}₫ tuần này!",
                'balanced_spender': f"⚖️ Balanced Spender - Cân bằng chi tiêu khá tốt!"
            }
        else:
            personality_labels = {
                'coffee_addict': f"☕ Coffee Addict - Spent {analysis['category_totals'].get('coffee', 0):,}₫ on coffee this week!",
                'foodie_explorer': f"🍜 Foodie Explorer - Food adventures cost {analysis['category_totals'].get('food', 0):,}₫!",
                'saving_master': f"💰 Saving Master - Saved {analysis['saving_total']:,}₫ this week!",
                'balanced_spender': f"⚖️ Balanced Spender - Pretty good balance!"
            }
        
        return personality_labels.get(personality, personality_labels['balanced_spender'])

    def get_spending_analysis(self) -> Dict[str, Any]:
        """Get detailed spending analysis for the week"""
        
        analysis = self._analyze_weekly_spending()
        personality = self._determine_personality(analysis)
        
        return {
            'analysis': analysis,
            'personality': personality,
            'insights': self._generate_insights(analysis, personality)
        }

    def _generate_insights(self, analysis: Dict[str, Any], personality: str) -> List[str]:
        """Generate spending insights"""
        
        insights = []
        
        if self.language == 'vi':
            # Category insights
            if analysis['dominant_category_amount'] > 0:
                insights.append(f"Category chi tiêu nhiều nhất: {analysis['dominant_category']} ({analysis['dominant_category_amount']:,}₫)")
            
            # Frequency insights
            if analysis['transaction_count'] > 20:
                insights.append(f"Bạn có {analysis['transaction_count']} giao dịch tuần này - khá tích cực!")
            elif analysis['transaction_count'] < 5:
                insights.append("Ít giao dịch tuần này - có thể bạn đang tiết kiệm?")
            
            # Net total insights
            if analysis['net_total'] > 0:
                insights.append(f"Tuyệt vời! Bạn có số dư dương {analysis['net_total']:,}₫ tuần này")
            else:
                insights.append("Chi tiêu nhiều hơn tiết kiệm tuần này")
        else:
            # English insights
            if analysis['dominant_category_amount'] > 0:
                insights.append(f"Top spending category: {analysis['dominant_category']} ({analysis['dominant_category_amount']:,}₫)")
            
            if analysis['transaction_count'] > 20:
                insights.append(f"You had {analysis['transaction_count']} transactions this week - quite active!")
            elif analysis['transaction_count'] < 5:
                insights.append("Few transactions this week - maybe you're saving?")
            
            if analysis['net_total'] > 0:
                insights.append(f"Great! You have positive balance of {analysis['net_total']:,}₫ this week")
            else:
                insights.append("Spent more than saved this week")
        
        return insights
