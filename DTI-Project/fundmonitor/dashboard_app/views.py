from django.shortcuts import render
from django.http import HttpResponse
import csv
from django.shortcuts import render, redirect, get_object_or_404
from .models import BankStatement, Staff
from .forms import StaffForm
from .models import Supplier
from .forms import SupplierForm
from .models import FundSource
from .forms import FundSourceForm
from .forms import BankStatementForm

# Create your views here.

# List all staff
def staff_list(request):
    staff_members = Staff.objects.all().order_by('last_name', 'first_name')
    
    # Calculate metrics
    staff_count = staff_members.count()
    divisions = staff_members.values_list('division', flat=True).distinct()
    divisions_count = len(divisions)
    
    context = {
        'staff_members': staff_members,
        'staff_count': staff_count,
        'divisions_count': divisions_count,
        'divisions': sorted(divisions),
    }
    return render(request, 'staff_list.html', context)

# Add new staff
def staff_add(request):
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = StaffForm()
    return render(request, 'staff_form.html', {'form': form})

# Edit existing staff
def staff_edit(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'staff_form.html', {'form': form})

# Delete staff
def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        return redirect('staff')
    return render(request, 'staff_confirm_delete.html', {'staff': staff})

    
def dashboard(request):
    return render(request, 'dashboard.html')

def mooe_report(request):
    return render(request, 'tin.html')

def tin(request):
    return render(request, 'tin.html')

def fund_report(request):
    return render(request, 'fund_report.html')

def mooe_report(request):
    return render(request, 'mooe_report.html')

def nc_report(request):
    return render(request, 'negosyo_center_report.html')

import json

def expense_report(request):
    # placeholder dataset for demonstration; replace with real query logic later
    report_data = [
        {
            'name': 'Traveling Expenses - Local',
            'months': {
                'Jan': 58408.31,
                'Feb': 0,
                'Mar': 0,
                'Apr': 0,
                'May': 0,
                'Jun': 0,
                'Jul': 0,
                'Aug': 0,
                'Sep': 0,
                'Oct': 58408.31,
                'Nov': 0,
                'Dec': 0,
            }
        },
        {
            'name': 'Training Expenses',
            'months': {
                'Jan': 33330.12,
                'Feb': 0,
                'Mar': 0,
                'Apr': 0,
                'May': 0,
                'Jun': 0,
                'Jul': 0,
                'Aug': 0,
                'Sep': 0,
                'Oct': 33330.12,
                'Nov': 0,
                'Dec': 0,
            }
        }
    ]
    # the template will use json_script to safely embed the array
    return render(request, 'expenses_report.html', {'report_data': report_data})



def mooe_report(request):
    months = [
        "Jan","Feb","Mar","1st Qtr",
        "Apr","May","Jun","2nd Qtr",
        "Jul","Aug","Sep","3rd Qtr",
        "Oct","Nov","Dec","4th Qtr"
    ]
    return render(request, "mooe_report.html", {"months": months})

def nc_report(request):
    months = [
        "Jan","Feb","Mar","1st Qtr",
        "Apr","May","Jun","2nd Qtr",
        "Jul","Aug","Sep","3rd Qtr",
        "Oct","Nov","Dec","4th Qtr"
    ]
    return render(request, "negosyo_center_report.html", {"months": months})

def fund_report(request):
    months = [
        "Jan","Feb","Mar","1st Qtr",
        "Apr","May","Jun","2nd Qtr",
        "Jul","Aug","Sep","3rd Qtr",
        "Oct","Nov","Dec","4th Qtr"
    ]
    return render(request, "fund_report.html", {"months": months})



def download_mooe(request, report_type):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{report_type}_report.csv"'

    writer = csv.writer(response)
    writer.writerow(['Month','OO1','OO2','OO3','4.1A','4.1B','4.2','Total'])

    months = [
        "Jan","Feb","Mar","1st Qtr",
        "Apr","May","Jun","2nd Qtr",
        "Jul","Aug","Sep","3rd Qtr",
        "Oct","Nov","Dec","4th Qtr"
    ]

    for m in months:
        writer.writerow([m,0,0,0,0,0,0,0])

    return response

# LIST
def supplier_list(request):
    suppliers = Supplier.objects.all()
    supplier_count = suppliers.count()
    vat_v_count = suppliers.filter(vat_status='V').count()
    vat_nv_count = suppliers.filter(vat_status='NV').count()
    
    context = {
        'suppliers': suppliers,
        'supplier_count': supplier_count,
        'vat_v_count': vat_v_count,
        'vat_nv_count': vat_nv_count,
    }
    return render(request, 'supplier_list.html', context)


# CREATE
def supplier_add(request):
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    return render(request, 'supplier_form.html', {'form': form})


# UPDATE
def supplier_edit(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'supplier_form.html', {'form': form})


# DELETE
def supplier_delete(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')

    return render(request, 'supplier_confirm_delete.html', {'supplier': supplier})


def fund_sources_view(request):
    funds = FundSource.objects.all()
    return render(request, 'fund_sources.html', {'funds': funds})



# LIST
def fund_sources_view(request):
    from django.db.models import Sum
    funds = FundSource.objects.all()
    
    # Calculate totals
    total_budget = funds.aggregate(total=Sum('annual_budget'))['total'] or 0
    fund_count = funds.count()
    average_budget = total_budget / fund_count if fund_count > 0 else 0
    
    context = {
        'funds': funds,
        'total_budget': total_budget,
        'fund_count': fund_count,
        'average_budget': average_budget,
    }
    return render(request, 'fund_sources.html', context)


# CREATE
def fund_source_create(request):
    if request.method == 'POST':
        form = FundSourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fund_sources')
    else:
        form = FundSourceForm()

    return render(request, 'fund_source_form.html', {'form': form})


# UPDATE
def fund_source_update(request, pk):
    fund = get_object_or_404(FundSource, pk=pk)

    if request.method == 'POST':
        form = FundSourceForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            return redirect('fund_sources')
    else:
        form = FundSourceForm(instance=fund)

    return render(request, 'fund_source_form.html', {'form': form})


# DELETE
def fund_source_delete(request, pk):
    fund = get_object_or_404(FundSource, pk=pk)

    if request.method == 'POST':
        fund.delete()
        return redirect('fund_sources')

    return render(request, 'fund_source_confirm_delete.html', {'fund': fund})



# LIST
def bank_statement_list(request):
    from django.db.models import Sum, Q
    statements = BankStatement.objects.all().order_by('-date')
    
    # Calculate totals
    debits = statements.filter(debit__gt=0).aggregate(total=Sum('debit'))['total'] or 0
    credits = statements.filter(credit__gt=0).aggregate(total=Sum('credit'))['total'] or 0
    
    context = {
        'statements': statements,
        'total_debits': debits,
        'total_credits': credits,
        'statement_count': statements.count(),
    }
    return render(request, 'bank_statement.html', context)


# CREATE
def bank_statement_create(request):
    if request.method == 'POST':
        form = BankStatementForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm()

    return render(request, 'bank_statement_form.html', {'form': form})


# UPDATE
def bank_statement_update(request, pk):
    statement = get_object_or_404(BankStatement, pk=pk)

    if request.method == 'POST':
        form = BankStatementForm(request.POST, instance=statement)
        if form.is_valid():
            form.save()
            return redirect('bank_statement_list')
    else:
        form = BankStatementForm(instance=statement)

    return render(request, 'bank_statement_form.html', {'form': form})


# DELETE
def bank_statement_delete(request, pk):
    statement = get_object_or_404(BankStatement, pk=pk)

    if request.method == 'POST':
        statement.delete()
        return redirect('bank_statement_list')

    return render(request, 'bank_statement_confirm_delete.html', {'statement': statement})