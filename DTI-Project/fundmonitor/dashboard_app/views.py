from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import datetime, timedelta
from decimal import Decimal
import json

from core.models import FundSource, Transaction, Supplier, Staff
from dashboard_app.models import MasterFundMonitoring, BankStatement, ExpenseObject


@login_required
def dashboard(request):
    """Main dashboard view with analytics data"""
    current_year = timezone.now().year
    
    # Get filter parameters from request
    selected_year = request.GET.get('year', current_year)
    selected_fund_source = request.GET.get('fund_source', '')
    selected_division = request.GET.get('division', '')
    selected_date_month = request.GET.get('date_month', '')
    
    # Build base queryset
    fund_sources = FundSource.objects.filter(year=selected_year)
    transactions = Transaction.objects.filter(fund_source__year=selected_year)
    
    # Apply filters
    if selected_fund_source:
        fund_sources = fund_sources.filter(id=selected_fund_source)
        transactions = transactions.filter(fund_source_id=selected_fund_source)
    if selected_division:
        transactions = transactions.filter(division=selected_division)
    if selected_date_month:
        transactions = transactions.filter(date__month=selected_date_month)
    
    # Calculate KPI metrics
    total_budget = fund_sources.aggregate(Sum('annual_budget'))['annual_budget__sum'] or Decimal('0')
    total_disbursement = transactions.aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
    remaining_balance = total_budget - total_disbursement
    budget_utilization_rate = round((float(total_disbursement) / float(total_budget) * 100), 1) if total_budget > 0 else 0
    active_fund_count = fund_sources.count()
    active_total_budget = fund_sources.aggregate(Sum('annual_budget'))['annual_budget__sum'] or Decimal('0')
    total_transactions = transactions.count()
    total_suppliers_paid = transactions.values('supplier').distinct().count()
    
    # Get monthly disbursement data
    monthly_data = {}
    for month in range(1, 13):
        monthly_data[str(month)] = float(
            transactions.filter(date__month=month).aggregate(Sum('payment_amount'))['payment_amount__sum'] or 0
        )
    
    # Get fund source breakdown
    fund_labels = [f.name for f in FundSource.objects.filter(year=selected_year)]
    fund_values = []
    for fund in FundSource.objects.filter(year=selected_year):
        remaining = fund.annual_budget - (transactions.filter(fund_source=fund).aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0'))
        fund_values.append(float(remaining))
    
    # Get budget vs disbursement
    budget_labels = [f.name for f in FundSource.objects.filter(year=selected_year)]
    budget_amounts = [float(f.annual_budget) for f in FundSource.objects.filter(year=selected_year)]
    disburse_amounts = []
    for fund in FundSource.objects.filter(year=selected_year):
        disbursed = transactions.filter(fund_source=fund).aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
        disburse_amounts.append(float(disbursed))
    
    # Get purchase type breakdown
    expense_labels = transactions.values_list('purchase_type', flat=True).distinct()[:5]
    expense_values = []
    for ptype in expense_labels:
        amount = transactions.filter(purchase_type=ptype).aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
        expense_values.append(float(amount))
    
    # Get top suppliers
    supplier_labels = []
    supplier_values = []
    top_suppliers = Supplier.objects.annotate(
        total_spent=Sum('transaction__payment_amount', filter=Q(transaction__in=transactions))
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:10]
    for supplier in top_suppliers:
        supplier_labels.append(supplier.name)
        supplier_values.append(float(supplier.total_spent or 0))
    
    # Get tax withholding data
    tax_labels = transactions.values_list('tax_type', flat=True).distinct()[:3]
    tax_values = []
    for ttype in tax_labels:
        amount = transactions.filter(tax_type=ttype).aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
        tax_values.append(float(amount))
    
    # Get cheque status
    cheque_labels = ['Cleared', 'Pending']
    cleared = transactions.filter(cleared_date__isnull=False).count()
    pending = transactions.filter(cleared_date__isnull=True).count()
    cheque_counts = [cleared, pending]
    
    # Get division spending
    division_labels = transactions.values_list('division', flat=True).distinct()
    division_values = []
    for div in division_labels:
        amount = transactions.filter(division=div).aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
        division_values.append(float(amount))
    
    # Get monthly balance trend (simplified)
    bank_dates = [d.isoformat() for d in [timezone.now().date()]]
    bank_debits = [0]
    bank_credits = [float(total_disbursement)]
    bank_balances = [float(remaining_balance)]
    
    # Get filter options
    years = FundSource.objects.values_list('year', flat=True).distinct().order_by('-year')
    divisions = transactions.values_list('division', flat=True).distinct()
    
    context = {
        'total_budget': total_budget,
        'total_disbursement': total_disbursement,
        'remaining_balance': remaining_balance,
        'budget_utilization_rate': budget_utilization_rate,
        'active_fund_count': active_fund_count,
        'active_total_budget': active_total_budget,
        'total_transactions': total_transactions,
        'total_suppliers_paid': total_suppliers_paid,
        'monthly_data': json.dumps(monthly_data),
        'fund_labels': json.dumps(fund_labels),
        'fund_values': json.dumps(fund_values),
        'budget_labels': json.dumps(budget_labels),
        'budget_amounts': json.dumps(budget_amounts),
        'disburse_amounts': json.dumps(disburse_amounts),
        'expense_labels': json.dumps(list(expense_labels)),
        'expense_values': json.dumps(expense_values),
        'supplier_labels': json.dumps(supplier_labels),
        'supplier_values': json.dumps(supplier_values),
        'tax_labels': json.dumps(list(tax_labels) if tax_labels else ['No Tax Data']),
        'tax_values': json.dumps(tax_values),
        'cheque_labels': json.dumps(cheque_labels),
        'cheque_counts': json.dumps(cheque_counts),
        'district_labels': json.dumps(list(division_labels)),
        'district_values': json.dumps(division_values),
        'bank_dates': json.dumps(bank_dates),
        'bank_debits': json.dumps(bank_debits),
        'bank_credits': json.dumps(bank_credits),
        'bank_balances': json.dumps(bank_balances),
        'years': years,
        'fund_sources': fund_sources,
        'divisions': divisions,
        'selected_year': selected_year,
        'selected_fund_source': selected_fund_source,
        'selected_division': selected_division,
        'selected_date_month': selected_date_month,
    }
    
    return render(request, 'dashboard.html', context)


@login_required
def get_dashboard_data(request):
    """API endpoint that returns JSON data for all dashboard charts"""
    
    current_year = timezone.now().year
    
    # Get all fund sources
    fund_sources = FundSource.objects.filter(year=current_year)
    
    # Calculate overall metrics
    total_budget = fund_sources.aggregate(Sum('annual_budget'))['annual_budget__sum'] or Decimal('0')
    
    all_transactions = Transaction.objects.filter(
        fund_source__year=current_year
    )
    total_disbursement = all_transactions.aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
    current_balance = total_budget - total_disbursement
    
    # Budget Utilization Rate
    bur_percentage = (float(total_disbursement) / float(total_budget) * 100) if total_budget > 0 else 0
    
    data = {
        'summary': {
            'total_budget': float(total_budget),
            'total_disbursement': float(total_disbursement),
            'current_balance': float(current_balance),
            'bur_percentage': round(bur_percentage, 2),
        },
        'fund_status': get_fund_status_data(current_year),
        'monthly_disbursement': get_monthly_disbursement_data(current_year),
        'supplier_spending': get_supplier_spending_data(current_year),
        'fund_breakdown': get_fund_breakdown_data(current_year),
        'payment_status': get_payment_status_data(current_year),
        'cheque_status': get_cheque_status_data(current_year),
        'expense_by_supplier': get_top_suppliers_data(current_year),
    }
    
    return JsonResponse(data)


def get_fund_status_data(year):
    """Get fund-wise budget and disbursement"""
    fund_sources = FundSource.objects.filter(year=year)
    
    fund_data = []
    for fund in fund_sources:
        disbursement = Transaction.objects.filter(
            fund_source=fund
        ).aggregate(Sum('payment_amount'))['payment_amount__sum'] or Decimal('0')
        
        balance = fund.annual_budget - disbursement
        bur = (float(disbursement) / float(fund.annual_budget) * 100) if fund.annual_budget > 0 else 0
        
        fund_data.append({
            'name': fund.name,
            'budget': float(fund.annual_budget),
            'disbursement': float(disbursement),
            'balance': float(balance),
            'bur_percentage': round(bur, 2),
        })
    
    return fund_data


def get_monthly_disbursement_data(year):
    """Get disbursement trends by month"""
    transactions = Transaction.objects.filter(
        fund_source__year=year
    ).order_by('date')
    
    monthly_data = {}
    for month in range(1, 13):
        monthly_data[month] = Decimal('0')
    
    for trans in transactions:
        month = trans.date.month
        monthly_data[month] += trans.payment_amount
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    return {
        'months': months,
        'data': [float(monthly_data[i]) for i in range(1, 13)]
    }


def get_supplier_spending_data(year):
    """Get spending by supplier"""
    suppliers = Supplier.objects.annotate(
        total_spent=Sum('transaction__payment_amount', filter=Q(transaction__fund_source__year=year))
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:10]
    
    return {
        'suppliers': [s.name for s in suppliers],
        'spending': [float(s.total_spent or 0) for s in suppliers]
    }


def get_fund_breakdown_data(year):
    """Get budget distribution across funds"""
    funds = FundSource.objects.filter(year=year)
    
    return {
        'funds': [f.name for f in funds],
        'budgets': [float(f.annual_budget) for f in funds]
    }


def get_payment_status_data(year):
    """Get payment status distribution"""
    transactions = Transaction.objects.filter(fund_source__year=year)
    
    statuses = {}
    for trans in transactions:
        status = trans.cheque_status or 'Pending'
        if status not in statuses:
            statuses[status] = 0
        statuses[status] += 1
    
    return {
        'statuses': list(statuses.keys()),
        'counts': list(statuses.values())
    }


def get_cheque_status_data(year):
    """Get cheque status breakdown"""
    transactions = Transaction.objects.filter(
        fund_source__year=year,
        cheque_number__isnull=False
    ).exclude(cheque_number='')
    
    cleared = transactions.filter(cleared_date__isnull=False).count()
    pending = transactions.filter(cleared_date__isnull=True).count()
    
    return {
        'cleared': cleared,
        'pending': pending,
        'total': cleared + pending
    }


def get_top_suppliers_data(year):
    """Get top 5 suppliers by spending"""
    suppliers = Supplier.objects.annotate(
        total_spent=Sum('transaction__payment_amount', filter=Q(transaction__fund_source__year=year))
    ).filter(total_spent__isnull=False).order_by('-total_spent')[:5]
    
    return {
        'suppliers': [s.name for s in suppliers],
        'amounts': [float(s.total_spent or 0) for s in suppliers]
    }
