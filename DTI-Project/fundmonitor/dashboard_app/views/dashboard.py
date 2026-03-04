from django.shortcuts import render
from django.db.models import Sum, Count, Q, F
from django.utils.timezone import now
from django.http import JsonResponse
import json
from decimal import Decimal
from dashboard_app.models import (
    MasterFundMonitoring, FundSource, Supplier, 
    ExpenseObject, Staff
)


def dashboard(request):
    """
    Main dashboard view with comprehensive analytics.
    Provides data for charts and key metrics.
    """
    current_year = now().year
    
    # ====== KEY METRICS ======
    total_transactions = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).count()
    
    total_payments = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    # Second highest metric - could be cleared transactions
    cleared_transactions = MasterFundMonitoring.objects.filter(
        date__year=current_year,
        cheque_status='Cleared'
    ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    fund_sources_count = FundSource.objects.all().count()
    suppliers_count = Supplier.objects.count()
    staff_count = Staff.objects.count()
    
    # ====== MONTHLY TREND DATA ======
    monthly_data = {}
    for month in range(1, 13):
        month_sum = MasterFundMonitoring.objects.filter(
            date__year=current_year,
            date__month=month
        ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
        month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                      'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        monthly_data[month_names[month - 1]] = float(month_sum)
    
    # ====== EXPENSE OBJECT BREAKDOWN ======
    expense_breakdown = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).values('account_title__name', 'account_title__color').annotate(
        total=Sum('payments')
    ).order_by('-total')[:10]
    
    expense_labels = [item['account_title__name'] for item in expense_breakdown]
    expense_values = [float(item['total'] or 0) for item in expense_breakdown]
    expense_colors = [item['account_title__color'] or '#0066FF' for item in expense_breakdown]
    
    # ====== FUND SOURCE DISTRIBUTION ======
    fund_distribution = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).values('fund_source__name').annotate(
        total=Sum('payments')
    ).order_by('-total')
    
    fund_labels = [item['fund_source__name'] for item in fund_distribution]
    fund_values = [float(item['total'] or 0) for item in fund_distribution]
    
    # ====== TOP SUPPLIERS ======
    top_suppliers = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).values('payee__supplier').annotate(
        total=Sum('payments')
    ).order_by('-total')[:10]
    
    supplier_labels = [item['payee__supplier'] for item in top_suppliers]
    supplier_values = [float(item['total'] or 0) for item in top_suppliers]
    
    # ====== PURCHASE TYPE DISTRIBUTION ======
    purchase_types = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).values('purchase_type__name').annotate(
        total=Sum('payments'),
        count=Count('id')
    ).order_by('-total')
    
    purchase_labels = [item['purchase_type__name'] or 'Not Specified' for item in purchase_types]
    purchase_values = [float(item['total'] or 0) for item in purchase_types]
    
    # ====== CHEQUE STATUS ======
    cheque_status = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).values('cheque_status').annotate(
        count=Count('id'),
        total=Sum('payments')
    ).order_by('-count')
    
    cheque_labels = [item['cheque_status'] or 'Not Specified' for item in cheque_status]
    cheque_counts = [item['count'] for item in cheque_status]
    
    context = {
        # Key Metrics
        'total_transactions': total_transactions,
        'total_payments': float(total_payments),
        'total_downloads': float(cleared_transactions),
        'fund_sources_count': fund_sources_count,
        'suppliers_count': suppliers_count,
        'staff_count': staff_count,
        
        # Chart Data
        'monthly_data': json.dumps(monthly_data),
        'expense_labels': json.dumps(expense_labels),
        'expense_values': json.dumps(expense_values),
        'expense_colors': json.dumps(expense_colors),
        'fund_labels': json.dumps(fund_labels),
        'fund_values': json.dumps(fund_values),
        'supplier_labels': json.dumps(supplier_labels),
        'supplier_values': json.dumps(supplier_values),
        'purchase_labels': json.dumps(purchase_labels),
        'purchase_values': json.dumps(purchase_values),
        'cheque_labels': json.dumps(cheque_labels),
        'cheque_counts': json.dumps(cheque_counts),
        'current_year': current_year,
    }
    
    return render(request, 'dashboard.html', context)


def get_dashboard_data(request):
    """
    API endpoint for dashboard data (JSON format).
    Used for dynamic updates if needed.
    """
    current_year = now().year
    
    # Calculate metrics
    total_transactions = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).count()
    
    total_payments = MasterFundMonitoring.objects.filter(
        date__year=current_year
    ).aggregate(total=Sum('payments'))['total'] or Decimal(0)
    
    data = {
        'total_transactions': total_transactions,
        'total_payments': float(total_payments),
        'year': current_year,
    }
    
    return JsonResponse(data)
