"""Fund Source Views - CRUD operations and breakdown management"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Q
from django.urls import reverse
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.contrib import messages
from dashboard_app.models import FundSource, FundSourceBreakdown, BreakdownCategory
from dashboard_app.forms import FundSourceForm, FundSourceBreakdownForm


def fund_sources_view(request):
    """List all fund sources with statistics and search support"""
    all_funds = FundSource.objects.all()
    
    # Get search query from URL parameter
    search_query = request.GET.get('q', '').strip()
    is_searching = bool(search_query)
    
    # Apply search filter if query exists
    if search_query:
        all_funds = all_funds.filter(
            Q(name__icontains=search_query)
        )
    
    # Calculate totals
    total_budget = all_funds.aggregate(total=Sum('annual_budget'))['total'] or 0
    fund_count = all_funds.count()
    
    # Calculate active funds (those with budget > 0)
    active_funds = all_funds.filter(annual_budget__gt=0)
    active_fund_count = active_funds.count()
    active_total_budget = active_funds.aggregate(total=Sum('annual_budget'))['total'] or 0
    
    average_budget = total_budget / fund_count if fund_count > 0 else 0
    
    # Pagination: 50 items per page (only when NOT searching)
    if is_searching:
        # Show all results when searching without pagination
        funds = all_funds
        paginator = None
    else:
        paginator = Paginator(all_funds, 50)
        page_number = request.GET.get('page', 1)
        funds = paginator.get_page(page_number)
    
    # Prepare page object
    if is_searching:
        page_obj = None
    else:
        page_obj = funds
    
    context = {
        'funds': funds,
        'total_budget': total_budget,
        'fund_count': fund_count,
        'active_fund_count': active_fund_count,
        'active_total_budget': active_total_budget,
        'average_budget': average_budget,
        'page_obj': page_obj,
        'paginator': paginator,
        'search_query': search_query,
        'is_searching': is_searching,
    }
    return render(request, 'funding/fund_source/fund_sources.html', context)



def fund_source_create(request):
    """Create new fund source"""
    if request.method == 'POST':
        form = FundSourceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fund_sources')
    else:
        form = FundSourceForm()

    return render(request, 'funding/fund_source/fund_source_form.html', {'form': form})


def fund_source_update(request, pk):
    """Update existing fund source"""
    fund = get_object_or_404(FundSource, pk=pk)

    if request.method == 'POST':
        form = FundSourceForm(request.POST, instance=fund)
        if form.is_valid():
            form.save()
            return redirect('fund_sources')
    else:
        form = FundSourceForm(instance=fund)

    return render(request, 'funding/fund_source/fund_source_form.html', {'form': form})


def fund_source_delete(request, pk):
    fund = get_object_or_404(FundSource, pk=pk)
    
    if request.method == 'POST':
        fund.delete()
        return redirect('fund_sources')
    
    object_details = {
        'Name': fund.name,
        'Annual Budget': f"${fund.annual_budget:,.2f}",
    }
    
    context = {
        'object_type': 'Fund Source',
        'item_label': fund.name,
        'item_name': 'fund source',
        'back_url': reverse('fund_sources'),
        'delete_url': reverse('fund_source_delete', args=[pk]),
        'object_details': object_details,
    }
    
    return render(request, 'components/confirm_delete.html', context)

def fund_source_detail(request, pk):
    """View fund source details including breakdowns"""
    fund = get_object_or_404(FundSource, pk=pk)
    breakdowns = fund.breakdowns.all()
    total_breakdown = breakdowns.aggregate(total=Sum('budget_amount'))['total'] or 0
    remaining_budget = fund.annual_budget - total_breakdown
    over_budget_amount = max(0, total_breakdown - fund.annual_budget)
    
    # Check if all categories have budgets allocated
    all_categories = BreakdownCategory.objects.count()
    allocated_categories = breakdowns.count()
    all_categories_allocated = all_categories > 0 and all_categories == allocated_categories
    
    context = {
        'fund': fund,
        'breakdowns': breakdowns,
        'total_breakdown': total_breakdown,
        'remaining_budget': remaining_budget,
        'over_budget_amount': over_budget_amount,
        'all_categories_allocated': all_categories_allocated,
    }
    return render(request, 'funding/fund_source/fund_source_detail.html', context)


def fund_source_breakdown_add(request, fund_id):
    """Add breakdown for a fund source"""
    fund = get_object_or_404(FundSource, pk=fund_id)
    total_breakdown = fund.breakdowns.aggregate(total=Sum('budget_amount'))['total'] or 0
    remaining_budget = fund.annual_budget - total_breakdown
    
    if request.method == 'POST':
        form = FundSourceBreakdownForm(request.POST, fund_source=fund)
        if form.is_valid():
            try:
                breakdown = form.save(commit=False)
                breakdown.fund_source = fund
                breakdown.save()
                messages.success(request, f'✓ Breakdown {breakdown.category.code} added successfully (₱{breakdown.budget_amount:,.2f})')
                return redirect('fund_source_detail', pk=fund_id)
            except IntegrityError:
                form.add_error(None, f'This category already has a breakdown allocated. Please select a different category or edit the existing allocation.')
    else:
        form = FundSourceBreakdownForm(fund_source=fund)
    
    context = {
        'fund': fund,
        'form': form,
        'total_breakdown': total_breakdown,
        'remaining_budget': remaining_budget,
    }
    return render(request, 'funding/fund_source/fund_source_breakdown_form.html', context)


def fund_source_breakdown_edit(request, pk):
    """Edit breakdown for a fund source"""
    breakdown = get_object_or_404(FundSourceBreakdown, pk=pk)
    fund = breakdown.fund_source
    total_breakdown = fund.breakdowns.exclude(id=pk).aggregate(total=Sum('budget_amount'))['total'] or 0
    remaining_budget = fund.annual_budget - total_breakdown
    
    if request.method == 'POST':
        form = FundSourceBreakdownForm(request.POST, instance=breakdown, fund_source=fund)
        if form.is_valid():
            try:
                form.save()
                messages.success(request, f'✓ Breakdown updated successfully (₱{breakdown.budget_amount:,.2f})')
                return redirect('fund_source_detail', pk=fund.id)
            except IntegrityError:
                form.add_error(None, f'This category allocation cannot be modified due to a conflict. Please refresh and try again.')
    else:
        form = FundSourceBreakdownForm(instance=breakdown, fund_source=fund)
    
    context = {
        'fund': fund,
        'breakdown': breakdown,
        'form': form,
        'total_breakdown': total_breakdown,
        'remaining_budget': remaining_budget,
    }
    return render(request, 'funding/fund_source/fund_source_breakdown_form.html', context)


def fund_source_breakdown_delete(request, pk):
    """Delete breakdown for a fund source"""
    import json
    from django.http import JsonResponse
    
    breakdown = get_object_or_404(FundSourceBreakdown, pk=pk)
    fund_id = breakdown.fund_source.id
    
    if request.method == 'POST':
        try:
            breakdown.delete()
            
            # Check if this is an AJAX request (JSON content-type or X-Requested-With header)
            is_ajax = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Content-Type', '')
            )
            
            if is_ajax:
                return JsonResponse({
                    'status': 'success',
                    'message': f'Breakdown deleted successfully',
                    'redirect_url': reverse('fund_source_detail', args=[fund_id])
                })
            
            # Handle regular form submissions
            return redirect('fund_source_detail', pk=fund_id)
        except Exception as e:
            is_ajax = (
                request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
                'application/json' in request.headers.get('Content-Type', '')
            )
            
            if is_ajax:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Error deleting breakdown: {str(e)}'
                }, status=400)
            return redirect('fund_source_detail', pk=fund_id)
