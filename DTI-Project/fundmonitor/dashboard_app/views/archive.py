"""Archive management views"""

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django.urls import reverse
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect

from bank_statement_app.models import BankStatement
from mater_fundmonitor_app.models import MasterFundMonitoring
from dashboard_app.utils.archive_utils import archive_by_year, unarchive_by_year, get_archive_stats
from user_app.utils import get_items_per_page


@login_required
def archive_dashboard(request):
    """Dashboard showing archive statistics and options"""
    
    # Get statistics
    stats = get_archive_stats()
    
    context = {
        'title': 'Archive Management',
        'stats': stats,
        'years_available': [2020, 2021, 2022, 2023, 2024, 2025, 2026, 2027],
    }
    
    return render(request, 'dashboard_app/archive/archived_dashboard.html', context)


@login_required
def archived_transactions(request):
    """View all archived transactions"""
    page_size = get_items_per_page(request)
    
    # Get archived transactions
    archived_records = MasterFundMonitoring.objects.all_with_archived().filter(
        is_archived=True
    ).order_by('-archived_at')
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    
    if search_query:
        archived_records = archived_records.filter(
            Q(payee__supplier__icontains=search_query) |
            Q(particulars__icontains=search_query) |
            Q(dv_number__icontains=search_query) |
            Q(cheque_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(archived_records, max(page_size, 1))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals
    total_result = archived_records.aggregate(total=Sum('payments'))['total']
    total_payments = float(total_result) if total_result is not None else 0.0
    
    context = {
        'title': 'Archived Transactions',
        'page_obj': page_obj,
        'search_query': search_query,
        'total_records': archived_records.count(),
        'total_payments': total_payments,
    }
    
    return render(request, 'dashboard_app/archive/archived_transactions.html', context)


@login_required
def archived_bank_statements(request):
    """View all archived bank statements"""
    page_size = get_items_per_page(request)
    
    # Get archived statements
    archived_records = BankStatement.objects.all_with_archived().filter(
        is_archived=True
    ).order_by('-archived_at')
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    
    if search_query:
        archived_records = archived_records.filter(
            Q(description__icontains=search_query) |
            Q(check_number__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(archived_records, max(page_size, 1))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate totals
    total_debit = archived_records.aggregate(total=Sum('debit'))['total']
    total_credit = archived_records.aggregate(total=Sum('credit'))['total']
    
    context = {
        'title': 'Archived Bank Statements',
        'page_obj': page_obj,
        'search_query': search_query,
        'total_records': archived_records.count(),
        'total_debit': float(total_debit) if total_debit is not None else 0.0,
        'total_credit': float(total_credit) if total_credit is not None else 0.0,
    }
    
    return render(request, 'dashboard_app/archive/archived_statements.html', context)


@login_required
@require_POST
@csrf_protect
def archive_year(request):
    """Archive all records for a specific year"""
    
    year = request.POST.get('year')
    reason = request.POST.get('reason', '')
    
    if not year:
        return JsonResponse({'error': 'Year is required'}, status=400)
    
    try:
        year = int(year)
        if year < 1900 or year > 2099:
            return JsonResponse({'error': 'Invalid year'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid year format'}, status=400)
    
    try:
        result = archive_by_year(year, user=request.user, reason=reason)

        return JsonResponse({
            'success': True,
            'result': result
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
@csrf_protect
def unarchive_year(request):
    """Unarchive all records for a specific year"""
    
    year = request.POST.get('year')
    
    if not year:
        return JsonResponse({'error': 'Year is required'}, status=400)
    
    try:
        year = int(year)
        if year < 1900 or year > 2099:
            return JsonResponse({'error': 'Invalid year'}, status=400)
    except ValueError:
        return JsonResponse({'error': 'Invalid year format'}, status=400)
    
    try:
        result = unarchive_by_year(year)

        return JsonResponse({
            'success': True,
            'result': result
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_POST
@csrf_protect
def unarchive_transaction(request, pk):
    """Unarchive a single transaction"""
    
    transaction = get_object_or_404(MasterFundMonitoring.objects.all_with_archived(), pk=pk)
    
    if not transaction.is_archived:
        messages.warning(request, 'Transaction is not archived')
        return redirect('archived_transactions')
    
    try:
        transaction.unarchive()
        return redirect('archived_transactions')
    except Exception as e:
        messages.error(request, f'Error restoring transaction: {str(e)}')
        return redirect('archived_transactions')


@login_required
@require_POST
@csrf_protect
def unarchive_statement(request, pk):
    """Unarchive a single bank statement"""
    
    statement = get_object_or_404(BankStatement.objects.all_with_archived(), pk=pk)
    
    if not statement.is_archived:
        messages.warning(request, 'Statement is not archived')
        return redirect('archived_statements')
    
    try:
        statement.unarchive()
        return redirect('archived_statements')
    except Exception as e:
        messages.error(request, f'Error restoring statement: {str(e)}')
        return redirect('archived_statements')


@login_required
def archive_stats_api(request):
    """API endpoint for archive statistics"""
    
    year = request.GET.get('year')
    
    if year:
        try:
            year = int(year)
        except ValueError:
            return JsonResponse({'error': 'Invalid year'}, status=400)
    
    stats = get_archive_stats(year)
    
    return JsonResponse(stats)
