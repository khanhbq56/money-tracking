from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db.models import Sum, Q, Count
from django.utils.translation import gettext as _
from django.shortcuts import get_object_or_404
from datetime import datetime, date
from collections import defaultdict
import calendar

from .models import Transaction, MonthlyTotal
from .serializers import (
    TransactionSerializer, TransactionCreateSerializer, TransactionListSerializer,
    MonthlyTotalSerializer, CalendarDataSerializer
)
from .monthly_service import MonthlyTotalService, update_monthly_totals_on_transaction_change
from .future_calculator import FutureProjectionCalculator


def index(request):
    """Main app view - Phase 3 implementation"""
    return render(request, 'index.html') 





class TransactionPagination(PageNumberPagination):
    """Custom pagination for transactions"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TransactionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Transaction CRUD operations with filtering and pagination.
    User authentication required and filters by current user.
    """
    serializer_class = TransactionSerializer
    pagination_class = TransactionPagination
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'expense_category']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date', '-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return TransactionCreateSerializer
        elif self.action == 'list':
            return TransactionListSerializer
        return TransactionSerializer
    
    def get_queryset(self):
        """Filter queryset based on query parameters and current user"""
        # Filter by current user only
        queryset = Transaction.objects.filter(user=self.request.user)
        
        # Filter by transaction type
        transaction_type = self.request.query_params.get('type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        
        # Filter by month and year
        month = self.request.query_params.get('month')
        year = self.request.query_params.get('year')
        if month and year:
            queryset = queryset.filter(date__year=year, date__month=month)
        
        # Filter by category (for expenses)
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(expense_category=category)
        
        return queryset
    
    def perform_create(self, serializer):
        """Create transaction and update monthly totals"""
        transaction = serializer.save(user=self.request.user)
        update_monthly_totals_on_transaction_change(transaction)
    
    def perform_update(self, serializer):
        """Update transaction and refresh monthly totals"""
        old_date = self.get_object().date
        transaction = serializer.save()
        
        # Update monthly totals for both old and new dates
        update_monthly_totals_on_transaction_change(transaction)
        if old_date != transaction.date:
            MonthlyTotalService.update_monthly_totals(self.request.user, old_date.year, old_date.month)
    
    def perform_destroy(self, instance):
        """Delete transaction and update monthly totals"""
        transaction_date = instance.date
        user = instance.user
        instance.delete()
        MonthlyTotalService.update_monthly_totals(user, transaction_date.year, transaction_date.month)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get transaction statistics"""
        queryset = self.get_queryset()
        
        # Overall statistics
        total_transactions = queryset.count()
        total_expense = abs(queryset.filter(transaction_type='expense').aggregate(
            total=Sum('amount'))['total'] or 0)
        total_saving = queryset.filter(transaction_type='saving').aggregate(
            total=Sum('amount'))['total'] or 0
        total_investment = queryset.filter(transaction_type='investment').aggregate(
            total=Sum('amount'))['total'] or 0
        
        # Category breakdown for expenses
        expense_categories = queryset.filter(transaction_type='expense').values(
            'expense_category').annotate(
            total=Sum('amount'), count=Count('id')).order_by('-total')
        
        # Calculate total money spent (all categories as positive)
        net_total = total_expense + total_saving + total_investment
        
        return Response({
            'total_transactions': total_transactions,
            'totals': {
                'expense': f"{total_expense:,.0f}₫",
                'saving': f"{total_saving:,.0f}₫",
                'investment': f"{total_investment:,.0f}₫",
                'net': f"{net_total:,.0f}₫"
            },
            'expense_categories': expense_categories
        })


@api_view(['GET'])
def calendar_data(request):
    """
    Get calendar data for a specific month and year.
    Requires authentication and filters by current user.
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': _('Authentication required')},
            status=status.HTTP_401_UNAUTHORIZED
        )
    """
    Get calendar data for a specific month and year.
    Query params: month (1-12), year (YYYY), filter (all|expense|saving|investment)
    """
    try:
        month = int(request.GET.get('month', datetime.now().month))
        year = int(request.GET.get('year', datetime.now().year))
        filter_type = request.GET.get('filter', 'all')
    except (ValueError, TypeError):
        return Response(
            {'error': _('Invalid month or year parameter')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Validate month and year
    if not (1 <= month <= 12):
        return Response(
            {'error': _('Month must be between 1 and 12')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not (2000 <= year <= 2100):
        return Response(
            {'error': _('Year must be between 2000 and 2100')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get transactions for the month (filtered by current user)
    transactions = Transaction.objects.filter(
        user=request.user,
        date__year=year,
        date__month=month
    )
    
    # Apply filter if specified
    if filter_type != 'all':
        transactions = transactions.filter(transaction_type=filter_type)
    
    # Group transactions by date
    transactions_by_date = defaultdict(list)
    for transaction in transactions:
        transactions_by_date[transaction.date].append(transaction)
    
    # Generate calendar data
    calendar_data = []
    
    # Get all days in the month
    month_range = calendar.monthrange(year, month)
    for day in range(1, month_range[1] + 1):
        current_date = date(year, month, day)
        day_transactions = transactions_by_date.get(current_date, [])
        
        # Calculate daily total
        daily_total = sum(t.amount for t in day_transactions)
        
        # Count transactions by type
        expense_count = sum(1 for t in day_transactions if t.transaction_type == 'expense')
        saving_count = sum(1 for t in day_transactions if t.transaction_type == 'saving')
        investment_count = sum(1 for t in day_transactions if t.transaction_type == 'investment')
        
        # Serialize transactions
        serialized_transactions = TransactionListSerializer(day_transactions, many=True).data
        
        calendar_data.append({
            'date': current_date,
            'transactions': serialized_transactions,
            'daily_total': daily_total,
            'expense_count': expense_count,
            'saving_count': saving_count,
            'investment_count': investment_count
        })
    
    # Serialize calendar data
    serializer = CalendarDataSerializer(calendar_data, many=True)
    
    return Response({
        'year': year,
        'month': month,
        'filter': filter_type,
        'calendar_data': serializer.data
    })


@api_view(['GET'])
def monthly_totals(request):
    """
    Get monthly totals for dashboard (user-specific).
    Query params: year (optional), month (optional)
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': _('Authentication required')},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    if year and month:
        try:
            year = int(year)
            month = int(month)
            totals = MonthlyTotalService.update_monthly_totals(request.user, year, month)
            serializer = MonthlyTotalSerializer(totals)
        except (ValueError, TypeError):
            return Response(
                {'error': _('Invalid year or month parameter')},
                status=status.HTTP_400_BAD_REQUEST
            )
    else:
        # Get current month totals for authenticated user
        totals_dict = MonthlyTotalService.get_current_month_totals(request.user)
        formatted = MonthlyTotalService.get_formatted_totals(request.user)
        
        return Response({
            'monthly_totals': totals_dict,
            'formatted': formatted,
            'year': datetime.now().year,
            'month': datetime.now().month
        })
    
    return Response(serializer.data)


@api_view(['PUT'])
def refresh_monthly_totals(request):
    """
    Force refresh of all monthly totals (admin only).
    """
    # Only allow superusers to refresh all monthly totals
    if not request.user.is_authenticated or not request.user.is_superuser:
        return Response(
            {'error': _('Admin access required')},
            status=status.HTTP_403_FORBIDDEN
        )
        
    try:
        updated_count = MonthlyTotalService.refresh_all_monthly_totals()
        return Response({
            'success': True,
            'message': _(f'Updated {updated_count} monthly totals'),
            'updated_count': updated_count
        })
    except Exception as e:
        return Response(
            {'error': _(f'Error refreshing monthly totals: {str(e)}')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def monthly_breakdown(request):
    """
    Get detailed monthly breakdown with categories (user-specific).
    Query params: year, month
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': _('Authentication required')},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    try:
        year = int(request.GET.get('year', datetime.now().year))
        month = int(request.GET.get('month', datetime.now().month))
    except (ValueError, TypeError):
        return Response(
            {'error': _('Invalid year or month parameter')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    breakdown = MonthlyTotalService.get_monthly_breakdown(request.user, year, month)
    
    return Response({
        'year': year,
        'month': month,
        'breakdown': breakdown
    })


@api_view(['GET'])
def today_summary(request):
    """
    Get summary of today's transactions (user-specific).
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': _('Authentication required')},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    today = date.today()
    transactions = Transaction.objects.filter(
        user=request.user,  # CRITICAL: Filter by user
        date=today
    )
    
    # Calculate totals
    total_expense = abs(transactions.filter(transaction_type='expense').aggregate(
        total=Sum('amount'))['total'] or 0)
    total_saving = transactions.filter(transaction_type='saving').aggregate(
        total=Sum('amount'))['total'] or 0
    total_investment = transactions.filter(transaction_type='investment').aggregate(
        total=Sum('amount'))['total'] or 0
    
    daily_total = total_saving + total_investment - total_expense
    
    # Serialize transactions
    serialized_transactions = TransactionListSerializer(transactions, many=True).data
    
    return Response({
        'date': today,
        'transactions': serialized_transactions,
        'totals': {
            'expense': f"-{total_expense:,.0f}₫",
            'saving': f"+{total_saving:,.0f}₫",
            'investment': f"+{total_investment:,.0f}₫",
            'daily_total': f"{'+' if daily_total >= 0 else ''}{daily_total:,.0f}₫"
        },
        'transaction_count': transactions.count()
    })


@api_view(['GET'])
def future_projection(request):
    """
    Get future financial projections with scenario analysis (user-specific).
    Query params: months (required, 1-60)
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': _('Authentication required')},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    try:
        months = int(request.GET.get('months', 12))
    except (ValueError, TypeError):
        return Response(
            {'error': _('Invalid months parameter')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not (1 <= months <= 60):
        return Response(
            {'error': _('Months must be between 1 and 60')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Simple mock projection when DB is empty or tables don't exist
        from django.db import connection
        from django.db.utils import OperationalError
        
        try:
            # Try to check if table exists
            with connection.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM transactions_transaction LIMIT 1")
            
            # Initialize calculator if table exists
            calculator = FutureProjectionCalculator(user=request.user)
            projection_data = calculator.calculate_projection(months)
            
        except OperationalError:
            # Return mock data if table doesn't exist
            projection_data = {
                'months': months,
                'display_text': f'{months} tháng tới',
                'base_projections': {
                    'expense': {'amount': 0, 'formatted': '0₫', 'monthly_avg': 0},
                    'saving': {'amount': 0, 'formatted': '0₫', 'monthly_avg': 0},
                    'investment': {'amount': 0, 'formatted': '0₫', 'monthly_avg': 0},
                    'net': {'amount': 0, 'formatted': '0₫', 'is_positive': True}
                },
                'scenarios': [],
                'goals': [],
                'patterns': {'monthly_averages': {'expense': 0, 'saving': 0, 'investment': 0}},
                'generated_at': datetime.now().isoformat()
            }
        
        return Response({
            'success': True,
            'data': projection_data
        })
        
    except Exception as e:
        return Response(
            {'error': _(f'Error calculating projection: {str(e)}')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def monthly_analysis(request):
    """
    Get detailed analysis for a specific month (user-specific).
    Query params: year (required), month (required)
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': _('Authentication required')},
            status=status.HTTP_401_UNAUTHORIZED
        )
        
    try:
        year = int(request.GET.get('year'))
        month = int(request.GET.get('month'))
    except (ValueError, TypeError):
        return Response(
            {'error': _('Year and month parameters are required')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not (1 <= month <= 12):
        return Response(
            {'error': _('Month must be between 1 and 12')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not (2000 <= year <= 2100):
        return Response(
            {'error': _('Year must be between 2000 and 2100')},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Initialize calculator
        calculator = FutureProjectionCalculator(user=request.user)
        
        # Get monthly analysis
        analysis_data = calculator.get_monthly_analysis(year, month)
        
        return Response({
            'success': True,
            'data': analysis_data
        })
        
    except Exception as e:
        return Response(
            {'error': _(f'Error analyzing month: {str(e)}')},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =============================================================================
# BANK INTEGRATION API VIEWS (Phase 2)
# =============================================================================

# Bank integration service - lazy import to avoid circular imports
BankIntegrationService = None

class BankSyncView(APIView):
    """Manual bank email sync endpoint"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Trigger manual bank sync"""
        try:
            # Lazy import bank integration service
            from .bank_integration_service import BankIntegrationService
            
            bank_code = request.data.get('bank_code')  # Optional: specific bank
            
            # Initialize bank integration service
            service = BankIntegrationService(request.user)
            
            # Perform sync
            result = service.sync_user_bank_emails(bank_code)
            
            if result.get('success'):
                return Response({
                    'success': True,
                    'message': _('Bank sync completed successfully'),
                    'data': result
                })
            else:
                return Response({
                    'success': False,
                    'error': result.get('error', 'Unknown error'),
                    'requires_gmail_auth': result.get('requires_gmail_auth', False)
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'error': f'Sync failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankSyncHistoryView(APIView):
    """Get bank sync history"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get sync history for user"""
        try:
            # Lazy import bank integration service
            from .bank_integration_service import BankIntegrationService
            
            bank_code = request.query_params.get('bank_code')
            limit = int(request.query_params.get('limit', 50))
            
            service = BankIntegrationService(request.user)
            history = service.get_sync_history(bank_code, limit)
            
            return Response({
                'success': True,
                'history': history
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class BankIntegrationTestView(APIView):
    """Test bank integration setup"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Test bank integration for a specific bank"""
        try:
            # Lazy import bank integration service
            from .bank_integration_service import BankIntegrationService
            
            bank_code = request.data.get('bank_code', 'tpbank')
            
            service = BankIntegrationService(request.user)
            test_result = service.test_bank_integration(bank_code)
            
            return Response({
                'success': True,
                'test_result': test_result
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 