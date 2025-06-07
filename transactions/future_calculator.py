from django.db.models import Sum, Avg, Count
from django.utils import timezone
from datetime import datetime, date, timedelta
from decimal import Decimal
from typing import Dict, List, Any
import json

from .models import Transaction


class FutureProjectionCalculator:
    """
    Calculate financial projections based on historical spending patterns
    and provide scenario analysis for future planning.
    """
    
    def __init__(self):
        self.analysis_months = 3  # Analyze last 3 months by default
        self.current_date = timezone.now().date()
    
    def calculate_projection(self, months: int) -> Dict[str, Any]:
        """
        Calculate financial projection for the given number of months.
        
        Args:
            months: Number of months to project into the future (1-60)
            
        Returns:
            Dict containing base projections, scenarios, and goal calculations
        """
        if not (1 <= months <= 60):
            raise ValueError("Months must be between 1 and 60")
        
        # Get historical patterns from last 3 months
        patterns = self._analyze_spending_patterns()
        
        # Calculate base projections
        base_projections = self._calculate_base_projections(patterns, months)
        
        # Calculate scenario variations
        scenarios = self._calculate_scenarios(patterns, months)
        
        # Calculate goal achievements
        goals = self._calculate_goal_achievements(patterns)
        
        return {
            'months': months,
            'display_text': self._format_timeline_display(months),
            'base_projections': base_projections,
            'scenarios': scenarios,
            'goals': goals,
            'patterns': patterns,
            'generated_at': timezone.now().isoformat()
        }
    
    def _analyze_spending_patterns(self) -> Dict[str, Any]:
        """Analyze spending patterns from the last 3 months"""
        end_date = self.current_date
        start_date = end_date - timedelta(days=90)  # Last 3 months
        
        transactions = Transaction.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        )
        
        # If no transactions in last 3 months, expand to last 6 months
        if transactions.count() == 0:
            start_date = end_date - timedelta(days=180)
            transactions = Transaction.objects.filter(
                date__gte=start_date,
                date__lte=end_date
            )
        
        # Calculate monthly averages by transaction type
        expense_avg = abs(transactions.filter(transaction_type='expense').aggregate(
            avg=Avg('amount'))['avg'] or 0)
        saving_avg = transactions.filter(transaction_type='saving').aggregate(
            avg=Avg('amount'))['avg'] or 0
        investment_avg = transactions.filter(transaction_type='investment').aggregate(
            avg=Avg('amount'))['avg'] or 0
        
        # Convert to float for consistent calculations
        expense_avg = float(expense_avg)
        saving_avg = float(saving_avg)
        investment_avg = float(investment_avg)
        
        # Analyze expense categories
        expense_categories = {}
        for category in ['coffee', 'food', 'transport', 'shopping', 'entertainment', 'health', 'education', 'utilities', 'other']:
            category_transactions = transactions.filter(
                transaction_type='expense',
                expense_category=category
            )
            category_avg = abs(category_transactions.aggregate(avg=Avg('amount'))['avg'] or 0)
            category_count = category_transactions.count()
            expense_categories[category] = {
                'monthly_avg': float(category_avg),
                'transaction_count': category_count,
                'percentage': (float(category_avg) / expense_avg * 100) if expense_avg > 0 else 0
            }
        
        # Calculate monthly transaction counts
        monthly_counts = transactions.values('date__year', 'date__month').annotate(
            count=Count('id')
        ).order_by('-date__year', '-date__month')
        
        avg_monthly_transactions = sum(item['count'] for item in monthly_counts) / max(len(monthly_counts), 1)
        
        return {
            'monthly_averages': {
                'expense': expense_avg,
                'saving': saving_avg,
                'investment': investment_avg
            },
            'expense_categories': expense_categories,
            'avg_monthly_transactions': avg_monthly_transactions,
            'analysis_period': {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat(),
                'days': 90
            }
        }
    
    def _calculate_base_projections(self, patterns: Dict, months: int) -> Dict[str, Any]:
        """Calculate base financial projections"""
        monthly_avg = patterns['monthly_averages']
        
        # Project based on current patterns
        projected_expense = monthly_avg['expense'] * months
        projected_saving = monthly_avg['saving'] * months
        projected_investment = monthly_avg['investment'] * months
        
        # Calculate net projection
        net_projection = projected_saving + projected_investment - projected_expense
        
        return {
            'expense': {
                'amount': float(projected_expense),
                'formatted': f"-{projected_expense:,.0f}₫",
                'monthly_avg': float(monthly_avg['expense'])
            },
            'saving': {
                'amount': float(projected_saving),
                'formatted': f"+{projected_saving:,.0f}₫",
                'monthly_avg': float(monthly_avg['saving'])
            },
            'investment': {
                'amount': float(projected_investment),
                'formatted': f"+{projected_investment:,.0f}₫",
                'monthly_avg': float(monthly_avg['investment'])
            },
            'net': {
                'amount': float(net_projection),
                'formatted': f"{'+' if net_projection >= 0 else ''}{net_projection:,.0f}₫",
                'is_positive': net_projection >= 0
            }
        }
    
    def _calculate_scenarios(self, patterns: Dict, months: int) -> List[Dict[str, Any]]:
        """Calculate 'What if' scenarios"""
        monthly_avg = patterns['monthly_averages']
        categories = patterns['expense_categories']
        
        scenarios = []
        
        # Scenario 1: Reduce coffee by 1 cup per day (assume 30k/cup, 30 days)
        coffee_savings_per_month = 30000 * 30  # 900k per month
        coffee_total_savings = coffee_savings_per_month * months
        scenarios.append({
            'name': 'reduce_coffee',
            'title': 'Nếu bớt coffee 1 ly/ngày',
            'description': 'Giảm 1 ly coffee mỗi ngày (30k/ly)',
            'savings_per_month': coffee_savings_per_month,
            'total_savings': coffee_total_savings,
            'formatted': f"+{coffee_total_savings:,.0f}₫",
            'impact': 'positive'
        })
        
        # Scenario 2: Cook more at home (reduce food expenses by 30%)
        food_monthly_avg = float(categories.get('food', {}).get('monthly_avg', 0))
        food_reduction = food_monthly_avg * 0.3
        home_cooking_savings = food_reduction * months
        scenarios.append({
            'name': 'cook_at_home',
            'title': 'Nếu ăn nhà thêm 2 bữa/tuần',
            'description': 'Giảm 30% chi phí ăn uống bằng cách nấu ăn tại nhà',
            'savings_per_month': food_reduction,
            'total_savings': home_cooking_savings,
            'formatted': f"+{home_cooking_savings:,.0f}₫",
            'impact': 'positive'
        })
        
        # Scenario 3: Increase investment by 500k per month
        extra_investment = 500000
        investment_increase = extra_investment * months
        scenarios.append({
            'name': 'increase_investment',
            'title': 'Nếu đầu tư thêm 500k/tháng',
            'description': 'Tăng đầu tư thêm 500,000₫ mỗi tháng',
            'savings_per_month': extra_investment,
            'total_savings': investment_increase,
            'formatted': f"+{investment_increase:,.0f}₫",
            'impact': 'investment'
        })
        
        # Scenario 4: Reduce transport costs (use bike/walk more)
        transport_monthly_avg = float(categories.get('transport', {}).get('monthly_avg', 0))
        transport_reduction = transport_monthly_avg * 0.25
        transport_savings = transport_reduction * months
        scenarios.append({
            'name': 'reduce_transport',
            'title': 'Nếu đi xe máy/đi bộ nhiều hơn',
            'description': 'Giảm 25% chi phí đi lại',
            'savings_per_month': transport_reduction,
            'total_savings': transport_savings,
            'formatted': f"+{transport_savings:,.0f}₫",
            'impact': 'positive'
        })
        
        return scenarios
    
    def _calculate_goal_achievements(self, patterns: Dict) -> List[Dict[str, Any]]:
        """Calculate how long it takes to achieve popular financial goals"""
        monthly_avg = patterns['monthly_averages']
        monthly_net = monthly_avg['saving'] + monthly_avg['investment'] - monthly_avg['expense']
        
        goals = [
            {'name': 'iphone_16_pro_max', 'title': 'iPhone 16 Pro Max', 'price': 34000000, 'icon': '📱'},
            {'name': 'honda_wave', 'title': 'Honda Wave RSX', 'price': 18000000, 'icon': '🏍️'},
            {'name': 'dalat_trip', 'title': 'Du lịch Đà Lạt', 'price': 5000000, 'icon': '🏔️'},
            {'name': 'emergency_fund', 'title': 'Quỹ khẩn cấp (6 tháng)', 'price': abs(monthly_avg['expense']) * 6, 'icon': '🚨'},
            {'name': 'laptop_macbook', 'title': 'MacBook Air M3', 'price': 28000000, 'icon': '💻'},
            {'name': 'motorbike_upgrade', 'title': 'Upgrade xe máy', 'price': 45000000, 'icon': '🏍️'}
        ]
        
        goal_results = []
        for goal in goals:
            if monthly_net > 0:
                months_needed = goal['price'] / monthly_net
                years = int(months_needed // 12)
                months_remainder = int(months_needed % 12)
                
                if months_needed < 1:
                    time_text = "Dưới 1 tháng"
                elif months_needed < 12:
                    time_text = f"{int(months_needed)} tháng"
                elif years > 0 and months_remainder > 0:
                    time_text = f"{years} năm {months_remainder} tháng"
                else:
                    time_text = f"{years} năm"
                    
                achievable = months_needed <= 60  # Reasonable timeframe
            else:
                time_text = "Không thể đạt được với mô hình chi tiêu hiện tại"
                achievable = False
                months_needed = float('inf')
            
            goal_results.append({
                'name': goal['name'],
                'title': goal['title'],
                'price': goal['price'],
                'icon': goal['icon'],
                'months_needed': float(months_needed) if months_needed != float('inf') else None,
                'time_text': time_text,
                'achievable': achievable,
                'formatted_price': f"{goal['price']:,.0f}₫"
            })
        
        # Sort by achievability and time needed
        goal_results.sort(key=lambda x: (not x['achievable'], x['months_needed'] if x['months_needed'] else float('inf')))
        
        return goal_results
    
    def _format_timeline_display(self, months: int) -> str:
        """Format timeline display text"""
        if months < 12:
            return f"{months} tháng"
        else:
            years = months // 12
            remaining_months = months % 12
            if remaining_months == 0:
                return f"{years} năm"
            else:
                return f"{years} năm {remaining_months} tháng"
    
    def get_monthly_analysis(self, year: int, month: int) -> Dict[str, Any]:
        """Get detailed analysis for a specific month"""
        transactions = Transaction.objects.filter(
            date__year=year,
            date__month=month
        )
        
        analysis = {
            'year': year,
            'month': month,
            'totals': {
                'expense': abs(transactions.filter(transaction_type='expense').aggregate(
                    total=Sum('amount'))['total'] or 0),
                'saving': transactions.filter(transaction_type='saving').aggregate(
                    total=Sum('amount'))['total'] or 0,
                'investment': transactions.filter(transaction_type='investment').aggregate(
                    total=Sum('amount'))['total'] or 0
            },
            'transaction_count': transactions.count(),
            'category_breakdown': {}
        }
        
        # Calculate net for the month
        analysis['totals']['net'] = (analysis['totals']['saving'] + 
                                   analysis['totals']['investment'] - 
                                   analysis['totals']['expense'])
        
        # Category breakdown for expenses
        for category in ['coffee', 'food', 'transport', 'shopping', 'entertainment', 'health', 'education', 'utilities', 'other']:
            category_total = abs(transactions.filter(
                transaction_type='expense',
                expense_category=category
            ).aggregate(total=Sum('amount'))['total'] or 0)
            
            analysis['category_breakdown'][category] = {
                'total': float(category_total),
                'formatted': f"{category_total:,.0f}₫"
            }
        
        return analysis
