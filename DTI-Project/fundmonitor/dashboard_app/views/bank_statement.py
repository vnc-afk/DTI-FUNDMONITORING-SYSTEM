"""Bank Statement Views - CRUD operations and transaction management"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.urls import reverse
from dashboard_app.models import BankStatement
from dashboard_app.forms import BankStatementForm


def bank_statement_list(request):
    """List all bank statements with statistics"""
    statements = BankStatement.objects.all().order_by('-date', '-created_at')
    
    # Calculate totals
    debits = statements.filter(debit__gt=0).aggregate(total=Sum('debit'))['total'] or 0
    credits = statements.filter(credit__gt=0).aggregate(total=Sum('credit'))['total'] or 0
    
    # Get latest statement for current values (by date and creation time)
    latest_statement = statements.first()
    current_debit = latest_statement.debit if latest_statement else 0
    current_credit = latest_statement.credit if latest_statement else 0
    current_balance = latest_statement.balance if latest_statement else 0
    
    context = {
        'statements': statements,
        'total_debits': debits,
        'total_credits': credits,
        'statement_count': statements.count(),
        'current_debit': current_debit,
        'current_credit': current_credit,
        'current_balance': current_balance,
        'statement_count': statements.count(),
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

    # For updates, always show as not first transaction (readonly)
    # Get the previous transaction's balance (before this one)
    previous_balance = 0
    transactions_before = BankStatement.objects.exclude(id=pk).order_by('-date', '-created_at')
    
    if transactions_before.exists():
        last_before = transactions_before.first()
        previous_balance = float(last_before.balance) if last_before else 0

    if request.method == 'POST':
        form = BankStatementForm(request.POST, instance=statement, is_first_transaction=False)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm(instance=statement, is_first_transaction=False)
    
    context = {
        'form': form,
        'is_first_transaction': False,
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
        'back_url': reverse('bank_statement_list'),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)

