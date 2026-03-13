from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
import json
from dashboard_app.models import Staff
from dashboard_app.forms import StaffForm


def staff_list(request):
    """List all staff members with search support"""
    all_staff_members = Staff.objects.all().order_by('last_name', 'first_name')
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    is_searching = bool(search_query)
    
    # Apply search filter if query exists
    if search_query:
        all_staff_members = all_staff_members.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(middle_initial__icontains=search_query) |
            Q(division__icontains=search_query)
        )
    
    # Calculate metrics
    staff_count = all_staff_members.count()
    divisions = list(all_staff_members.values_list('division', flat=True).distinct())
    divisions_count = len(divisions)
    
    # Prepare summary cards for component
    summary_cards = [
        {
            'label': 'Total Staff Members',
            'value': staff_count,
            'sublabel': 'Active personnel',
            'is_currency': False,
        },
        {
            'label': 'Total Divisions',
            'value': divisions_count,
            'sublabel': 'Departments',
            'is_currency': False,
        }
    ]
    
    # Prepare filter options for component
    division_filter_options = {division: division for division in sorted(divisions)}
    
    # Prepare toolbar count
    toolbar_count = f'{staff_count} staff member{"" if staff_count == 1 else "s"}'
    
    # Pagination: 50 items per page (only when NOT searching)
    if is_searching:
        # Show all results when searching without pagination
        staff_members = all_staff_members
        paginator = None
    else:
        paginator = Paginator(all_staff_members, 50)
        page_number = request.GET.get('page', 1)
        staff_members = paginator.get_page(page_number)
    
    # Prepare page object
    if is_searching:
        page_obj = None
    else:
        page_obj = staff_members
    
    context = {
        'staff_members': staff_members,
        'staff_count': staff_count,
        'divisions_count': divisions_count,
        'divisions': sorted(divisions),
        'summary_cards': summary_cards,
        'division_filter_options': division_filter_options,
        'toolbar_count': toolbar_count,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'is_searching': is_searching,
    }
    return render(request, 'staff/staff_list.html', context)



def staff_add(request):
    """Add new staff member"""
    if request.method == 'POST':
        form = StaffForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('staff')
    else:
        form = StaffForm()
    return render(request, 'staff/staff_form.html', {'form': form})


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
    return render(request, 'staff/staff_form.html', {'form': form})


def staff_delete(request, pk):
    staff = get_object_or_404(Staff, pk=pk)
    
    if request.method == 'POST':
        staff.delete()
        return redirect('staff')
    
    object_details = {
        'Name': f"{staff.first_name} {staff.last_name}",
        'Division': staff.division.name if staff.division else 'N/A',
    }
    
    context = {
        'object_type': 'Staff',
        'item_label': f"{staff.first_name} {staff.last_name}",
        'item_name': 'staff member',
        'back_url': reverse('staff'),
        'delete_url': reverse('staff_delete', args=[pk]),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)


@require_http_methods(["POST"])
def staff_bulk_delete(request):
    """Delete multiple staff members via AJAX"""
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        
        if not ids:
            return JsonResponse({'success': False, 'message': 'No ids provided'})
        
        # Ensure ids are integers
        ids = [int(id) for id in ids]
        
        # Delete the staff members
        deleted_count, _ = Staff.objects.filter(pk__in=ids).delete()
        
        return JsonResponse({
            'success': True,
            'message': f'{deleted_count} staff member(s) deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)