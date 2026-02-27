from django.shortcuts import render, redirect, get_object_or_404
from dashboard_app.models import Supplier
from dashboard_app.forms import SupplierForm


def supplier_list(request):
    """List all suppliers"""
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
    return render(request, 'supplier/list.html', context)


def supplier_add(request):
    """Add new supplier"""
    if request.method == 'POST':
        form = SupplierForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm()

    return render(request, 'supplier/form.html', {'form': form})


def supplier_edit(request, pk):
    """Edit existing supplier"""
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        form = SupplierForm(request.POST, instance=supplier)
        if form.is_valid():
            form.save()
            return redirect('supplier_list')
    else:
        form = SupplierForm(instance=supplier)

    return render(request, 'supplier/form.html', {'form': form})


def supplier_delete(request, pk):
    """Delete supplier"""
    supplier = get_object_or_404(Supplier, pk=pk)

    if request.method == 'POST':
        supplier.delete()
        return redirect('supplier_list')

    return render(request, 'supplier/confirm_delete.html', {'supplier': supplier})
