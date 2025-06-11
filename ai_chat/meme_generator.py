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
            },
            'distracted_boyfriend': {
                'name': 'Distracted Boyfriend',
                'image': 'distracted_boyfriend.jpg',
                'format': 'temptation',
                'personality_weights': {
                    'coffee_addict': 3,
                    'foodie_explorer': 3,
                    'saving_master': 1,
                    'balanced_spender': 2
                }
            },
            'two_buttons': {
                'name': 'Two Buttons',
                'image': 'two_buttons.jpg',
                'format': 'dilemma',
                'personality_weights': {
                    'coffee_addict': 2,
                    'foodie_explorer': 2,
                    'saving_master': 3,
                    'balanced_spender': 3
                }
            },
            'change_my_mind': {
                'name': 'Change My Mind',
                'image': 'change_my_mind.jpg',
                'format': 'statement',
                'personality_weights': {
                    'coffee_addict': 2,
                    'foodie_explorer': 2,
                    'saving_master': 3,
                    'balanced_spender': 2
                }
            },
            'woman_yelling_cat': {
                'name': 'Woman Yelling at Cat',
                'image': 'woman_yelling_cat.jpg',
                'format': 'confrontation',
                'personality_weights': {
                    'coffee_addict': 3,
                    'foodie_explorer': 2,
                    'saving_master': 1,
                    'balanced_spender': 2
                }
            },
            'stonks': {
                'name': 'Stonks',
                'image': 'stonks.jpg',
                'format': 'trend',
                'personality_weights': {
                    'coffee_addict': 1,
                    'foodie_explorer': 1,
                    'saving_master': 3,
                    'balanced_spender': 2
                }
            },
            'panik_kalm': {
                'name': 'Panik Kalm',
                'image': 'panik_kalm.jpg',
                'format': 'emotional_journey',
                'personality_weights': {
                    'coffee_addict': 2,
                    'foodie_explorer': 2,
                    'saving_master': 2,
                    'balanced_spender': 3
                }
            },
            'galaxy_brain': {
                'name': 'Galaxy Brain',
                'image': 'galaxy_brain.jpg',
                'format': 'enlightenment',
                'personality_weights': {
                    'coffee_addict': 3,
                    'foodie_explorer': 3,
                    'saving_master': 2,
                    'balanced_spender': 2
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
                    ],
                    'distracted_boyfriend': {
                        'boyfriend': 'Tôi',
                        'girlfriend': 'Kế hoạch tiết kiệm',
                        'other_woman': 'Coffee mới ra'
                    },
                    'two_buttons': {
                        'button1': 'Tiết kiệm tiền',
                        'button2': 'Uống coffee 5 ly/ngày'
                    },
                    'change_my_mind': 'Coffee không phải chi phí, đó là đầu tư năng suất',
                    'woman_yelling_cat': {
                        'woman': 'BẠN ĐÃ CHI BAO NHIÊU CHO COFFEE?!',
                        'cat': '...chỉ 375k thôi mà'
                    },
                    'stonks': 'Coffee addiction 📈',
                    'panik_kalm': {
                        'panik1': 'Nhìn bill coffee tuần này',
                        'kalm': 'Nhớ ra mình làm việc hiệu quả hơn',
                        'panik2': 'Bill tuần sau sẽ cao hơn'
                    },
                    'galaxy_brain': [
                        'Uống coffee để tỉnh táo',
                        'Uống coffee để networking',
                        'Uống coffee để sống còn',
                        'Coffee = oxygen'
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
                    ],
                    'distracted_boyfriend': {
                        'boyfriend': 'Tôi',
                        'girlfriend': 'Ngân sách ăn uống',
                        'other_woman': 'Quán mới viral'
                    },
                    'two_buttons': {
                        'button1': 'Nấu ăn tại nhà',
                        'button2': 'Thử quán mới mỗi ngày'
                    },
                    'change_my_mind': 'Ăn ngon là đầu tư cho hạnh phúc tinh thần',
                    'woman_yelling_cat': {
                        'woman': 'SAO LẠI CHI 1.2M CHO ĂN UỐNG?!',
                        'cat': '...nhưng mà ngon lắm'
                    },
                    'stonks': 'Food exploration 📈',
                    'panik_kalm': {
                        'panik1': 'Check bill ăn uống tuần này',
                        'kalm': 'Nhớ ra mình đã ăn những món ngon tuyệt vời',
                        'panik2': 'Tuần sau có thêm 5 quán mới'
                    },
                    'galaxy_brain': [
                        'Ăn để sống',
                        'Ăn để trải nghiệm',
                        'Ăn để check-in',
                        'Ăn = nghệ thuật sống'
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
                    ],
                    'distracted_boyfriend': {
                        'boyfriend': 'Tôi',
                        'girlfriend': 'Chi tiêu hợp lý',
                        'other_woman': 'Tiết kiệm tối đa'
                    },
                    'two_buttons': {
                        'button1': 'Mua đồ cần thiết',
                        'button2': 'Tiết kiệm thêm 100k nữa'
                    },
                    'change_my_mind': 'Tiết kiệm 50% thu nhập là bình thường',
                    'woman_yelling_cat': {
                        'woman': 'BẠN PHẢI SỐNG CUỘC SỐNG!',
                        'cat': '...nhưng mà tiết kiệm được 800k'
                    },
                    'stonks': 'Saving rate 📈',
                    'panik_kalm': {
                        'panik1': 'Nhìn người khác chi tiêu',
                        'kalm': 'Nhớ ra mình đã tiết kiệm được 80%',
                        'panik2': 'Họ sẽ nghĩ mình keo kiệt'
                    },
                    'galaxy_brain': [
                        'Tiết kiệm để mua nhà',
                        'Tiết kiệm để an toàn tài chính',
                        'Tiết kiệm để tự do tài chính',
                        'Tiết kiệm = tối cao'
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
                    ],
                    'distracted_boyfriend': {
                        'boyfriend': 'Tôi',
                        'girlfriend': 'Ngân sách cân bằng',
                        'other_woman': 'Sale 50% off'
                    },
                    'two_buttons': {
                        'button1': 'Chi tiêu theo kế hoạch',
                        'button2': 'Linh hoạt với ngân sách'
                    },
                    'change_my_mind': 'Cân bằng thu chi là chìa khóa hạnh phúc',
                    'woman_yelling_cat': {
                        'woman': 'BẠN QUẢN LÝ TIỀN NHƯ THẾ NÀO?',
                        'cat': '...vừa phải thôi'
                    },
                    'stonks': 'Financial balance 📊',
                    'panik_kalm': {
                        'panik1': 'Tháng này chi nhiều quá',
                        'kalm': 'Nhưng vẫn trong kế hoạch',
                        'panik2': 'Tháng sau phải cân bằng lại'
                    },
                    'galaxy_brain': [
                        'Chi tiêu có kế hoạch',
                        'Tiết kiệm có mục tiêu',
                        'Đầu tư có chiến lược',
                        'Tài chính = zen'
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
                    ],
                    'distracted_boyfriend': {
                        'boyfriend': 'Me',
                        'girlfriend': 'Balanced budget',
                        'other_woman': '50% off sale'
                    },
                    'two_buttons': {
                        'button1': 'Spend according to plan',
                        'button2': 'Be flexible with budget'
                    },
                    'change_my_mind': 'Balanced income-expense is the key to happiness',
                    'woman_yelling_cat': {
                        'woman': 'HOW DO YOU MANAGE YOUR MONEY?',
                        'cat': '...just moderate'
                    },
                    'stonks': 'Financial balance 📊',
                    'panik_kalm': {
                        'panik1': 'Spent too much this month',
                        'kalm': 'But still within plan',
                        'panik2': 'Need to rebalance next month'
                    },
                    'galaxy_brain': [
                        'Plan expenses',
                        'Save with goals',
                        'Invest with strategy',
                        'Finance = zen'
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
        
        personality_labels_map = {
            'vi': {
                'coffee_addict': f"☕ Coffee Addict - Chi {analysis['category_totals'].get('coffee', 0):,}₫ cho coffee tuần này!",
                'foodie_explorer': f"🍜 Foodie Explorer - Khám phá ẩm thực với {analysis['category_totals'].get('food', 0):,}₫!",
                'saving_master': f"💰 Saving Master - Tiết kiệm {analysis['saving_total']:,}₫ tuần này!",
                'balanced_spender': f"⚖️ Balanced Spender - Cân bằng chi tiêu khá tốt!"
            },
            'en': {
                'coffee_addict': f"☕ Coffee Addict - Spent {analysis['category_totals'].get('coffee', 0):,}₫ on coffee this week!",
                'foodie_explorer': f"🍜 Foodie Explorer - Food adventures cost {analysis['category_totals'].get('food', 0):,}₫!",
                'saving_master': f"💰 Saving Master - Saved {analysis['saving_total']:,}₫ this week!",
                'balanced_spender': f"⚖️ Balanced Spender - Pretty good balance!"
            }
        }
        
        personality_labels = personality_labels_map.get(self.language, personality_labels_map['vi'])
        
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
        
        insight_templates = {
            'vi': {
                'dominant_category': "Category chi tiêu nhiều nhất: {category} ({amount:,}₫)",
                'high_frequency': "Bạn có {count} giao dịch tuần này - khá tích cực!",
                'low_frequency': "Ít giao dịch tuần này - có thể bạn đang tiết kiệm?",
                'positive_balance': "Tuyệt vời! Bạn có số dư dương {amount:,}₫ tuần này",
                'negative_balance': "Chi tiêu nhiều hơn tiết kiệm tuần này"
            },
            'en': {
                'dominant_category': "Top spending category: {category} ({amount:,}₫)",
                'high_frequency': "You had {count} transactions this week - quite active!",
                'low_frequency': "Few transactions this week - maybe you're saving?",
                'positive_balance': "Great! You have positive balance of {amount:,}₫ this week",
                'negative_balance': "Spent more than saved this week"
            }
        }
        
        templates = insight_templates.get(self.language, insight_templates['vi'])
        
        # Category insights
        if analysis['dominant_category_amount'] > 0:
            insights.append(templates['dominant_category'].format(
                category=analysis['dominant_category'],
                amount=analysis['dominant_category_amount']
            ))
        
        # Frequency insights
        if analysis['transaction_count'] > 20:
            insights.append(templates['high_frequency'].format(count=analysis['transaction_count']))
        elif analysis['transaction_count'] < 5:
            insights.append(templates['low_frequency'])
        
        # Net total insights
        if analysis['net_total'] > 0:
            insights.append(templates['positive_balance'].format(amount=analysis['net_total']))
        else:
            insights.append(templates['negative_balance'])
        
        return insights
