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
    return render(request, 'dashboard.html')


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
