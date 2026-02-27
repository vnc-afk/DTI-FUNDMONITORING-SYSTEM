from django.shortcuts import render, redirect, get_object_or_404
from dashboard_app.models import Staff
from dashboard_app.forms import StaffForm


def staff_list(request):
    """List all staff members"""
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
    return render(request, 'staff/list.html', context)


def staff_add(request):
    """Add new staff member"""
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = StaffForm()
    return render(request, 'staff/form.html', {'form': form})


def staff_edit(request, pk):
    """Edit existing staff member"""
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        form = StaffForm(request.POST, instance=staff)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = StaffForm(instance=staff)
    return render(request, 'staff/form.html', {'form': form})


def staff_delete(request, pk):
    """Delete staff member"""
    staff = get_object_or_404(Staff, pk=pk)
    if request.method == 'POST':
        staff.delete()
        return redirect('staff')
    return render(request, 'staff/confirm_delete.html', {'staff': staff})
