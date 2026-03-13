"""Bank Statement Views - CRUD operations and transaction management"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
import json
from dashboard_app.models import BankStatement
from dashboard_app.forms import BankStatementForm


def bank_statement_list(request):
    """List all bank statements with statistics and search support"""
    all_statements = BankStatement.objects.all().order_by('-date', '-created_at')
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    is_searching = bool(search_query)
    
    # Apply search filter if query exists
    if search_query:
        all_statements = all_statements.filter(
            Q(description__icontains=search_query) |
            Q(check_number__icontains=search_query) |
            Q(date__icontains=search_query)
        )
    
    # Calculate totals
    debits = all_statements.filter(debit__gt=0).aggregate(total=Sum('debit'))['total'] or 0
    credits = all_statements.filter(credit__gt=0).aggregate(total=Sum('credit'))['total'] or 0
    
    # Get latest statement for current values (by date and creation time)
    latest_statement = all_statements.first()
    current_debit = latest_statement.debit if latest_statement else 0
    current_credit = latest_statement.credit if latest_statement else 0
    current_balance = latest_statement.balance if latest_statement else 0
    
    # Prepare summary cards for component
    summary_cards = [
        {
            'label': 'Current Debit',
            'value': current_debit,
            'sublabel': 'Latest transaction',
            'is_currency': True,
            'css_class': 'debit',
        },
        {
            'label': 'Current Credit',
            'value': current_credit,
            'sublabel': 'Latest transaction',
            'is_currency': True,
            'css_class': 'credit',
        },
        {
            'label': 'Current Balance',
            'value': current_balance,
            'sublabel': 'As of today',
            'is_currency': True,
            'css_class': 'balance',
        }
    ]
    
    # Prepare filter options for component
    status_filter_options = {
        'cleared': 'Cleared',
        'on process': 'On Process',
        'failed': 'Failed',
    }
    
    # Prepare toolbar count
    statement_count = all_statements.count()
    toolbar_count = f'{statement_count} entr{"y" if statement_count == 1 else "ies"}'
    
    # Pagination: 50 items per page (only when NOT searching)
    if is_searching:
        # Show all results when searching without pagination
        statements = all_statements
        paginator = None
    else:
        paginator = Paginator(all_statements, 50)
        page_number = request.GET.get('page', 1)
        statements = paginator.get_page(page_number)
    
    # Prepare page object
    if is_searching:
        page_obj = None
    else:
        page_obj = statements
    
    context = {
        'statements': statements,
        'total_debits': debits,
        'total_credits': credits,
        'statement_count': statement_count,
        'current_debit': current_debit,
        'current_credit': current_credit,
        'current_balance': current_balance,
        'summary_cards': summary_cards,
        'status_filter_options': status_filter_options,
        'toolbar_count': toolbar_count,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'is_searching': is_searching,
    }
    return render(request, 'funding/bank_statement/bank_statement.html', context)



def bank_statement_create(request):
    """Create new bank statement"""
    # Check if there are existing transactions
    has_existing = BankStatement.objects.exists()
    previous_balance = 0
    
    if has_existing:
        # Get the last transaction's balance
        last_statement = BankStatement.objects.order_by('-date', '-created_at').first()
        previous_balance = float(last_statement.balance) if last_statement else 0
    
    if request.method == 'POST':
        form = BankStatementForm(request.POST, is_first_transaction=not has_existing)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm(is_first_transaction=not has_existing)
    
    context = {
        'form': form,
        'is_first_transaction': not has_existing,
        'previous_balance': previous_balance,
    }
    return render(request, 'funding/bank_statement/bank_statement_form.html', context)


def bank_statement_update(request, pk):
    """Update existing bank statement"""
    statement = get_object_or_404(BankStatement, pk=pk)

    # Check if this is the first chronological transaction
    first_transaction = BankStatement.objects.order_by('date', 'created_at').first()
    is_first_transaction = first_transaction and first_transaction.id == pk
    
    # Get the previous transaction's balance (before this one chronologically)
    previous_balance = 0
    # Get transactions that come BEFORE this one by date and creation time
    transactions_before = BankStatement.objects.exclude(id=pk).filter(
        date__lt=statement.date
    ) | BankStatement.objects.exclude(id=pk).filter(
        date=statement.date, created_at__lt=statement.created_at
    )
    
    if transactions_before.exists():
        # Get the last transaction chronologically before this one
        last_before = transactions_before.order_by('-date', '-created_at').first()
        previous_balance = float(last_before.balance) if last_before else 0

    if request.method == 'POST':
        form = BankStatementForm(request.POST, instance=statement, is_first_transaction=is_first_transaction)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm(instance=statement, is_first_transaction=is_first_transaction)
    
    context = {
        'form': form,
        'is_first_transaction': is_first_transaction,
        'previous_balance': previous_balance,
    }
    return render(request, 'funding/bank_statement/bank_statement_form.html', context)

def bank_statement_delete(request, pk):
    statement = get_object_or_404(BankStatement, pk=pk)
    
    if request.method == 'POST':
        statement.delete()
        return redirect('bank_statement_list')
    
    object_details = {
        'Date': statement.date.strftime('%b %d, %Y'),
        'Description': statement.description,
        'Check Number': statement.check_number,
        'Debit': f"₱ {statement.debit:,.2f}",
        'Credit': f"₱ {statement.credit:,.2f}",
        'Balance': f"₱ {statement.balance:,.2f}",
        'Status': statement.status,
    }
    
    context = {
        'object_type': 'Bank Statement',
        'item_label': f"Statement from {statement.date.strftime('%b %d, %Y')}",
        'item_name': 'bank statement',
        'back_url': reverse('bank_statement_list'),
        'delete_url': reverse('bank_statement_delete', args=[pk]),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)


@require_http_methods(["POST"])
def bank_statement_bulk_delete(request):
    """Delete multiple bank statements via AJAX"""
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({'success': False, 'message': 'No ids provided'})
        
        # Ensure ids are integers
        ids = [int(id) for id in ids]
        
        # Delete the statements
        deleted_count, _ = BankStatement.objects.filter(pk__in=ids).delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} statement(s) deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@require_http_methods(["POST"])
def bank_statement_update_status(request, pk):
    """Update bank statement status via AJAX"""
    try:
        statement = get_object_or_404(BankStatement, pk=pk)
        data = json.loads(request.body)
        new_status = data.get('status')
        
        # Validate status
        valid_statuses = ['Cleared', 'On Process']
        if new_status not in valid_statuses:
            return JsonResponse({
                'success': False,
                'message': f'Invalid status. Must be one of: {", ".join(valid_statuses)}'
            }, status=400)
        
        statement.status = new_status
        statement.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Status updated to {new_status}',
            'status': statement.status
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)

