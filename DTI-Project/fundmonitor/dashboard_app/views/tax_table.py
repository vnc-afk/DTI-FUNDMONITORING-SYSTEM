"""Tax Table Views - CRUD operations for tax rates"""

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from dashboard_app.models import TaxTable
from dashboard_app.forms import TaxTableForm


def tax_table_list(request):
    """List all tax table entries"""
    entries = TaxTable.objects.all()
    count = entries.count()
    context = {
        'entries': entries,
        'entry_count': count,
    }
    return render(request, 'funding/tax/tax_table.html', context)


def tax_table_create(request):
    """Create new tax table entry"""
    if request.method == 'POST':
        form = TaxTableForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('tax_table')
    else:
        form = TaxTableForm()
    return render(request, 'funding/tax/tax_form.html', {'form': form})


def tax_table_update(request, pk):
    """Update existing tax table entry"""
    entry = get_object_or_404(TaxTable, pk=pk)
    if request.method == 'POST':
        form = TaxTableForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            return redirect('tax_table')
    else:
        form = TaxTableForm(instance=entry)
    return render(request, 'funding/tax/tax_form.html', {'form': form})


def tax_table_delete(request, pk):
    tax_table = get_object_or_404(TaxTable, pk=pk)
    
    if request.method == 'POST':
        tax_table.delete()
        return redirect('tax_table_list')
    
    object_details = {
        'Purchase Type': tax_table.purchase_type.name if tax_table.purchase_type else 'N/A',
        'VAT Goods (5%)': tax_table.vat_goods_5 or 'N/A',
        'VAT Services (5%)': tax_table.vat_services_5 or 'N/A',
        'VAT Goods & Services (3%)': tax_table.vat_goods_services_3 or 'N/A',
        'VAT Goods (1%)': tax_table.vat_goods_1 or 'N/A',
        'VAT Services (2%)': tax_table.vat_services_2 or 'N/A',
        'VAT Rental (5%)': tax_table.vat_rental_5 or 'N/A',
        'VAT Professional Fee (10%)': tax_table.vat_prof_fee_10 or 'N/A',       
    }
    
    context = {
        'object_type': 'Tax Table Entry',
        'back_url': reverse('tax_table'),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)