"""Fund Source Views - CRUD operations and breakdown management"""

from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.urls import reverse
from dashboard_app.models import FundSource, FundSourceBreakdown
from dashboard_app.forms import FundSourceForm, FundSourceBreakdownForm


def fund_sources_view(request):
    """List all fund sources with statistics"""
    from django.db.models import Q
    
    funds = FundSource.objects.all()
    
    # Calculate totals
    total_budget = funds.aggregate(total=Sum('annual_budget'))['total'] or 0
    fund_count = funds.count()
    
    # Calculate active funds (those with budget > 0)
    active_funds = funds.filter(annual_budget__gt=0)
    active_fund_count = active_funds.count()
    active_total_budget = active_funds.aggregate(total=Sum('annual_budget'))['total'] or 0
    
    average_budget = total_budget / fund_count if fund_count > 0 else 0
    
    context = {
        'funds': funds,
        'total_budget': total_budget,
        'fund_count': fund_count,
        'active_fund_count': active_fund_count,
        'active_total_budget': active_total_budget,
        'average_budget': average_budget,
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
        'back_url': reverse('fund_sources'),
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
    
    context = {
        'fund': fund,
        'breakdowns': breakdowns,
        'total_breakdown': total_breakdown,
        'remaining_budget': remaining_budget,
        'over_budget_amount': over_budget_amount,
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
            breakdown = form.save(commit=False)
            breakdown.fund_source = fund
            breakdown.save()
            return redirect('fund_source_detail', pk=fund_id)
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
            form.save()
            return redirect('fund_source_detail', pk=fund.id)
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
    breakdown = get_object_or_404(FundSourceBreakdown, pk=pk)
    fund_id = breakdown.fund_source.id
    
    if request.method == 'POST':
        breakdown.delete()
        return redirect('fund_source_detail', pk=fund_id)
    
    context = {
        'breakdown': breakdown,
        'fund': breakdown.fund_source,
    }
    return render(request, 'funding/fund_source/fund_source_breakdown_confirm_delete.html', context)
