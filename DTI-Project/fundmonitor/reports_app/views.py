import csv
import json
from decimal import Decimal

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.timezone import now

from data_management_app.models import District, FundSource, NegosyoCenter
from mater_fundmonitor_app.models import MasterFundMonitoring


def expense_report(request):
	"""Generate expense report grouped by classification or object of expense."""
	from data_management_app.models import ExpenseCategory, ExpenseObject

	group_by = request.GET.get('group_by', 'classification')
	is_object_grouping = group_by == 'object'

	if is_object_grouping:
		groups = ExpenseObject.objects.filter(is_active=True).values('id', 'code', 'name', 'color')
		group_fk = 'account_title_id'
		group_label = 'Object of Expense'
		search_placeholder = 'Search object of expense...'
	else:
		groups = ExpenseCategory.objects.filter(is_active=True).values('id', 'name', 'color')
		group_fk = 'expense_classification_id'
		group_label = 'Expense Category'
		search_placeholder = 'Search expense category...'

	current_year = now().year
	expense_data = []

	for group in groups:
		filter_kwargs = {group_fk: group['id'], 'date__year': current_year}
		expenses = MasterFundMonitoring.objects.filter(**filter_kwargs).values_list('date', 'payments')

		q1 = [Decimal(0), Decimal(0), Decimal(0)]
		q2 = [Decimal(0), Decimal(0), Decimal(0)]
		q3 = [Decimal(0), Decimal(0), Decimal(0)]
		q4 = [Decimal(0), Decimal(0), Decimal(0)]

		for date, payment in expenses:
			if date and payment:
				month = date.month - 1
				quarter_idx = month // 3
				month_in_quarter = month % 3

				if quarter_idx == 0:
					q1[month_in_quarter] += Decimal(str(payment))
				elif quarter_idx == 1:
					q2[month_in_quarter] += Decimal(str(payment))
				elif quarter_idx == 2:
					q3[month_in_quarter] += Decimal(str(payment))
				elif quarter_idx == 3:
					q4[month_in_quarter] += Decimal(str(payment))

		expense_data.append(
			{
				'name': f"({group['code']}) {group['name']}" if is_object_grouping else group['name'],
				'color': group['color'],
				'q1': [float(x) for x in q1],
				'q2': [float(x) for x in q2],
				'q3': [float(x) for x in q3],
				'q4': [float(x) for x in q4],
			}
		)

	# Include transactions with no selected grouping value so they are not excluded.
	unclassified_filter = {'date__year': current_year}
	unclassified_filter['account_title__isnull' if is_object_grouping else 'expense_classification__isnull'] = True
	unclassified_expenses = MasterFundMonitoring.objects.filter(
		**unclassified_filter,
	).values_list('date', 'payments')

	if unclassified_expenses:
		q1 = [Decimal(0), Decimal(0), Decimal(0)]
		q2 = [Decimal(0), Decimal(0), Decimal(0)]
		q3 = [Decimal(0), Decimal(0), Decimal(0)]
		q4 = [Decimal(0), Decimal(0), Decimal(0)]

		for date, payment in unclassified_expenses:
			if date and payment:
				month = date.month - 1
				quarter_idx = month // 3
				month_in_quarter = month % 3

				if quarter_idx == 0:
					q1[month_in_quarter] += Decimal(str(payment))
				elif quarter_idx == 1:
					q2[month_in_quarter] += Decimal(str(payment))
				elif quarter_idx == 2:
					q3[month_in_quarter] += Decimal(str(payment))
				elif quarter_idx == 3:
					q4[month_in_quarter] += Decimal(str(payment))

		expense_data.append(
			{
				'name': 'Unclassified / Not Assigned',
				'color': '#6c757d',
				'q1': [float(x) for x in q1],
				'q2': [float(x) for x in q2],
				'q3': [float(x) for x in q3],
				'q4': [float(x) for x in q4],
			}
		)

	expense_json = json.dumps(expense_data)

	return render(
		request,
		'reports_app/reports/expenses_report.html',
		{
			'current_year': current_year,
			'group_by': 'object' if is_object_grouping else 'classification',
			'group_label': group_label,
			'search_placeholder': search_placeholder,
			'report_data': expense_data,
			'expense_json': expense_json,
		},
	)


def mooe_report(request):
	"""Generate MOOE (Maintenance and Other Operating Expenses) report."""
	from data_management_app.models import BreakdownCategory, FundSourceBreakdown

	month_names = [
		'Jan',
		'Feb',
		'Mar',
		'Apr',
		'May',
		'Jun',
		'Jul',
		'Aug',
		'Sep',
		'Oct',
		'Nov',
		'Dec',
	]

	categories = BreakdownCategory.objects.filter(is_active=True).order_by('order', 'code')
	category_codes = ['OO1', 'OO2', 'OO3', '4.1A', '4.1B', '4.2']

	budget_data = {}
	grand_total_budget = Decimal(0)
	grand_total_disbursed = Decimal(0)

	for cat in categories:
		annual_budget = (
			FundSourceBreakdown.objects.filter(category=cat).aggregate(total=Sum('budget_amount'))['total']
			or Decimal(0)
		)
		total_disbursed = (
			MasterFundMonitoring.objects.filter(mooe=cat.code).aggregate(total=Sum('payments'))['total']
			or Decimal(0)
		)

		current_balance = annual_budget - total_disbursed
		bur = (total_disbursed / annual_budget) * 100 if annual_budget > 0 else Decimal(0)

		budget_data[cat.code] = {
			'name': cat.name,
			'annual_budget': float(annual_budget),
			'total_disbursed': float(total_disbursed),
			'current_balance': float(current_balance),
			'bur': float(bur),
		}

		grand_total_budget += annual_budget
		grand_total_disbursed += total_disbursed

	grand_balance = grand_total_budget - grand_total_disbursed
	grand_bur = (grand_total_disbursed / grand_total_budget) * 100 if grand_total_budget > 0 else Decimal(0)

	current_year = now().year
	disbursement_data = {}
	downloads_data = {}

	for month_num in range(1, 13):
		disbursement_data[month_num] = {}
		downloads_data[month_num] = {}
		for code in category_codes:
			disbursement_data[month_num][code] = 0.0
			downloads_data[month_num][code] = 0.0

	for code in category_codes:
		for month_num in range(1, 13):
			monthly_payments = (
				MasterFundMonitoring.objects.filter(
					mooe=code,
					date__month=month_num,
					date__year=current_year,
				).aggregate(total=Sum('payments'))['total']
				or Decimal(0)
			)
			disbursement_data[month_num][code] = float(monthly_payments)

			monthly_downloads = (
				MasterFundMonitoring.objects.filter(
					mooe=code,
					date__month=month_num,
					date__year=current_year,
				).aggregate(total=Sum('downloads'))['total']
				or Decimal(0)
			)
			downloads_data[month_num][code] = float(monthly_downloads)

	disbursement_breakdown = []
	downloads_breakdown = []

	def calc_row_total(data_dict, codes):
		return sum(data_dict.get(code, 0) for code in codes)

	for month_num in range(1, 13):
		row_total = calc_row_total(disbursement_data[month_num], category_codes)
		disbursement_breakdown.append(
			{
				'month': month_names[month_num - 1],
				'month_num': month_num,
				'data': disbursement_data[month_num],
				'total': row_total,
				'quarter': None,
			}
		)

		row_total = calc_row_total(downloads_data[month_num], category_codes)
		downloads_breakdown.append(
			{
				'month': month_names[month_num - 1],
				'month_num': month_num,
				'data': downloads_data[month_num],
				'total': row_total,
				'quarter': None,
			}
		)

	mooe_report_data = {
		'categoryCodes': category_codes,
		'budgetData': budget_data,
		'disbursementBreakdown': disbursement_breakdown,
		'downloadsBreakdown': downloads_breakdown,
		'grandTotalBudget': float(grand_total_budget),
		'grandTotalDisbursed': float(grand_total_disbursed),
		'grandBalance': float(grand_balance),
		'grandBur': float(grand_bur),
	}

	context = {
		'mooe_report_data': mooe_report_data, 
		'grand_total_budget': float(grand_total_budget),
		'grand_total_disbursed': float(grand_total_disbursed),
		'grand_balance': float(grand_balance),
		'grand_bur': float(grand_bur),
	}
	return render(request, 'reports_app/reports/mooe_report.html', context)


def nc_report(request):
	"""Generate Negosyo Center report by district and municipality."""
	from datetime import datetime
	from data_management_app.models import District, FundSource

	current_year = datetime.now().year
	districts = District.objects.prefetch_related('negosyo_centers').order_by('order', 'name')

	month_names = [
		'January', 'February', 'March', 'April', 'May', 'June',
		'July', 'August', 'September', 'October', 'November', 'December',
	]

	districts_data = []
	total_disbursement = 0.0
	total_downloads = 0.0

	for district in districts:
		negosyo_centers = district.negosyo_centers.filter(is_active=True).order_by('name')
		if not negosyo_centers.exists():
			continue

		nc_ids = list(negosyo_centers.values_list('id', flat=True))
		transactions = MasterFundMonitoring.objects.filter(
			nc_id__in=nc_ids,
			date__year=current_year,
		).order_by('nc__name', 'date')

		# Use str(id) as keys throughout
		monthly_data = {m: {} for m in range(1, 13)}
		for nc in negosyo_centers:
			for month_num in range(1, 13):
				monthly_data[month_num][str(nc.id)] = 0.0  # ← str()

		for transaction in transactions:
			month_num = transaction.date.month
			nc_id = str(transaction.nc_id)  # ← str()
			payment = float(transaction.payments or 0)
			monthly_data[month_num][nc_id] += payment
			total_disbursement += payment
			total_downloads += float(transaction.downloads or 0)

		quarters = []
		quarter_configs = [
			{'months': [1, 2, 3], 'label': 'Q1', 'range': 'January - March'},
			{'months': [4, 5, 6], 'label': 'Q2', 'range': 'April - June'},
			{'months': [7, 8, 9], 'label': 'Q3', 'range': 'July - September'},
			{'months': [10, 11, 12], 'label': 'Q4', 'range': 'October - December'},
		]

		for qtr_config in quarter_configs:
			qtr_months = []
			qtr_total = 0

			for month_num in qtr_config['months']:
				month_row = {
					'name': month_names[month_num - 1],
					'month_num': month_num,
					'nc_data': {},
					'month_total': 0,
				}

				for nc in negosyo_centers:
					amount = monthly_data[month_num].get(str(nc.id), 0.0)  # ← str()
					month_row['nc_data'][str(nc.id)] = amount  # ← str()
					month_row['month_total'] += amount
					qtr_total += amount

				qtr_months.append(month_row)

			quarters.append({
				'label': qtr_config['label'],
				'range': qtr_config['range'],
				'months': qtr_months,
				'total': qtr_total,
			})

		districts_data.append({
			'name': district.name,
			'order': district.order,
			'negosyo_centers': [{'id': str(nc.id), 'name': nc.name} for nc in negosyo_centers],  # ← str()
			'quarters': quarters,
			'district_total': sum(q['total'] for q in quarters),
		})

	annual_budget = FundSource.objects.filter(
		name__icontains='negosyo center'
	).aggregate(total=Sum('annual_budget'))['total'] or Decimal(0)
	annual_budget = float(annual_budget)
	current_balance = annual_budget - total_disbursement
	bur_rate = (total_disbursement / annual_budget * 100) if annual_budget > 0 else 0

	nc_report_data = {
		'districts': districts_data,
		'totalDisbursement': total_disbursement,
		'totalDownloads': total_downloads,
		'annualBudget': annual_budget,
		'currentBalance': current_balance,
		'burRate': bur_rate,
	}

	context = {
		'nc_report_data': nc_report_data,
		'annual_budget': annual_budget,
		'total_disbursement': total_disbursement,
		'total_downloads': total_downloads,
		'current_balance': current_balance,
		'bur_rate': bur_rate,
	}
	return render(request, 'reports_app/reports/negosyo_center_report.html', context)


def fund_report(request):
	"""Generate fund report by fund source."""
	from datetime import datetime
	from data_management_app.models import FundSource

	month_names = [
		'Jan',
		'Feb',
		'Mar',
		'Apr',
		'May',
		'Jun',
		'Jul',
		'Aug',
		'Sep',
		'Oct',
		'Nov',
		'Dec',
	]

	fund_sources = FundSource.objects.filter(annual_budget__gt=0).order_by('name')
	fund_sources_with_data = FundSource.objects.filter(
		id__in=MasterFundMonitoring.objects.values_list('fund_source_id', flat=True).distinct()
	).order_by('name')

	all_fund_ids = set([f.id for f in fund_sources]) | set([f.id for f in fund_sources_with_data])
	fund_sources = FundSource.objects.filter(id__in=all_fund_ids).order_by('name')
	fund_codes = [fund.id for fund in fund_sources]
	current_year = datetime.now().year

	budget_data = {}
	grand_total_budget = 0
	grand_total_disbursed = 0
	grand_total_downloads = 0

	for fund in fund_sources:
		annual_budget = fund.annual_budget or 0
		total_disbursed = (
			MasterFundMonitoring.objects.filter(fund_source=fund).aggregate(total=Sum('payments'))['total'] or 0
		)
		total_downloads = (
			MasterFundMonitoring.objects.filter(fund_source=fund).aggregate(total=Sum('downloads'))['total'] or 0
		)

		current_balance = float(annual_budget) - float(total_disbursed)
		bur_percent = (float(total_disbursed) / float(annual_budget) * 100) if annual_budget > 0 else 0

		budget_data[fund.id] = {
			'annual_budget': float(annual_budget),
			'total_disbursed': float(total_disbursed),
			'total_downloads': float(total_downloads),
			'current_balance': current_balance,
			'bur_percent': bur_percent,
		}

		grand_total_budget += float(annual_budget)
		grand_total_disbursed += float(total_disbursed)
		grand_total_downloads += float(total_downloads)

	grand_total_balance = grand_total_budget - grand_total_disbursed
	grand_total_bur = (grand_total_disbursed / grand_total_budget * 100) if grand_total_budget > 0 else 0

	disbursement_data = {}
	downloads_data = {}

	for month_num in range(1, 13):
		disbursement_data[month_num] = {}
		downloads_data[month_num] = {}

		for fund in fund_sources:
			month_disbursement = (
				MasterFundMonitoring.objects.filter(
					fund_source=fund,
					date__month=month_num,
					date__year=current_year,
				).aggregate(total=Sum('payments'))['total']
				or 0
			)

			month_downloads = (
				MasterFundMonitoring.objects.filter(
					fund_source=fund,
					date__month=month_num,
					date__year=current_year,
				).aggregate(total=Sum('downloads'))['total']
				or 0
			)

			disbursement_data[month_num][str(fund.id)] = float(month_disbursement) 
			downloads_data[month_num][str(fund.id)] = float(month_downloads)  

	def calc_row_total(data_dict, codes):
		return sum(data_dict.get(code, 0) for code in codes)

	disbursement_breakdown = []
	downloads_breakdown = []

	for month_num in range(1, 13):
		row_total = calc_row_total(disbursement_data[month_num], fund_codes)
		disbursement_breakdown.append(
			{
				'month': month_names[month_num - 1],
				'month_num': month_num,
				'data': disbursement_data[month_num],
				'total': row_total,
				'quarter': None,
			}
		)

		row_total = calc_row_total(downloads_data[month_num], fund_codes)
		downloads_breakdown.append(
			{
				'month': month_names[month_num - 1],
				'month_num': month_num,
				'data': downloads_data[month_num],
				'total': row_total,
				'quarter': None,
			}
		)

	fund_report_data = {
		'funds': [{'id': str(f.id), 'name': f.name} for f in fund_sources],  
		'budgetData': {str(k): v for k, v in budget_data.items()},   
		'disbursementBreakdown': disbursement_breakdown,
		'downloadsBreakdown': downloads_breakdown,
		'grandTotalBudget': grand_total_budget,
		'grandTotalDisbursed': grand_total_disbursed,
		'grandTotalDownloads': grand_total_downloads,
		'grandTotalBalance': grand_total_balance,
		'grandTotalBur': grand_total_bur,
	}

	return render(
		request,
		'reports_app/reports/fund_report.html',
		{
			'fund_report_data': fund_report_data,
			'grand_total_budget': grand_total_budget,
			'grand_total_disbursed': grand_total_disbursed,
			'grand_total_downloads': grand_total_downloads,
			'grand_total_balance': grand_total_balance,
			'grand_total_bur': grand_total_bur,
		},
	)


def download_mooe(request, report_type):
	"""Download MOOE report (disbursement or downloads) as CSV."""
	from data_management_app.models import BreakdownCategory

	current_year = now().year
	month_names = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
		'July',
		'August',
		'September',
		'October',
		'November',
		'December',
	]

	categories = BreakdownCategory.objects.filter(is_active=True).order_by('order', 'code')

	if not categories.exists():
		category_codes = ['OO1', 'OO2', 'OO3', '4.1A', '4.1B', '4.2']
	else:
		category_codes = [cat.code for cat in categories]

	data = {}
	for month_num in range(1, 13):
		data[month_num] = {}
		for code in category_codes:
			data[month_num][code] = 0.0

	for code in category_codes:
		for month_num in range(1, 13):
			if report_type == 'disbursement':
				monthly_amount = (
					MasterFundMonitoring.objects.filter(
						mooe=code,
						date__month=month_num,
						date__year=current_year,
					).aggregate(total=Sum('payments'))['total']
					or Decimal(0)
				)
			else:
				monthly_amount = (
					MasterFundMonitoring.objects.filter(
						mooe=code,
						date__month=month_num,
						date__year=current_year,
					).aggregate(total=Sum('downloads'))['total']
					or Decimal(0)
				)

			data[month_num][code] = float(monthly_amount)

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="mooe_{report_type}_{current_year}.csv"'
	writer = csv.writer(response)
	report_title = 'Disbursement' if report_type == 'disbursement' else 'Downloads'

	writer.writerow([f'MOOE {report_title} Report - Fiscal Year {current_year}'])
	writer.writerow(['Month'] + category_codes + ['Total'])

	for month_num in range(1, 13):
		row = [month_names[month_num - 1]]
		month_total = 0
		for code in category_codes:
			amount = data[month_num][code]
			row.append(round(amount, 2))
			month_total += amount
		row.append(round(month_total, 2))
		writer.writerow(row)

	writer.writerow([])
	writer.writerow(['Quarterly Summary'])
	quarters = [('Q1', [1, 2, 3]), ('Q2', [4, 5, 6]), ('Q3', [7, 8, 9]), ('Q4', [10, 11, 12])]

	for q_label, q_months in quarters:
		row = [q_label]
		q_total = 0
		for code in category_codes:
			code_total = sum(data[m][code] for m in q_months)
			row.append(round(code_total, 2))
			q_total += code_total
		row.append(round(q_total, 2))
		writer.writerow(row)

	return response


def download_fund(request, report_type):
	"""Download Fund Report (disbursement or downloads) as CSV."""
	from data_management_app.models import FundSource

	current_year = now().year
	month_names = [
		'January',
		'February',
		'March',
		'April',
		'May',
		'June',
		'July',
		'August',
		'September',
		'October',
		'November',
		'December',
	]

	fund_sources = FundSource.objects.all().order_by('name')

	data = {}
	for month_num in range(1, 13):
		data[month_num] = {}
		for fund in fund_sources:
			data[month_num][fund.id] = 0.0

	for fund in fund_sources:
		for month_num in range(1, 13):
			if report_type == 'disbursement':
				monthly_amount = (
					MasterFundMonitoring.objects.filter(
						fund_source=fund,
						date__month=month_num,
						date__year=current_year,
					).aggregate(total=Sum('payments'))['total']
					or Decimal(0)
				)
			else:
				monthly_amount = (
					MasterFundMonitoring.objects.filter(
						fund_source=fund,
						date__month=month_num,
						date__year=current_year,
					).aggregate(total=Sum('downloads'))['total']
					or Decimal(0)
				)

			data[month_num][fund.id] = float(monthly_amount)

	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = f'attachment; filename="fund_{report_type}_{current_year}.csv"'
	writer = csv.writer(response)
	report_title = 'Disbursement' if report_type == 'disbursement' else 'Downloads'

	writer.writerow([f'Fund Report {report_title} - Fiscal Year {current_year}'])
	writer.writerow([])
	writer.writerow(['Month'] + [fund.name for fund in fund_sources] + ['Total'])

	for month_num in range(1, 13):
		row = [month_names[month_num - 1]]
		month_total = 0
		for fund in fund_sources:
			amount = data[month_num][fund.id]
			row.append(round(amount, 2))
			month_total += amount
		row.append(round(month_total, 2))
		writer.writerow(row)

	writer.writerow([])
	writer.writerow(['Quarterly Summary'])
	quarters = [('Q1', [1, 2, 3]), ('Q2', [4, 5, 6]), ('Q3', [7, 8, 9]), ('Q4', [10, 11, 12])]

	for q_label, q_months in quarters:
		row = [q_label]
		q_total = 0
		for fund in fund_sources:
			fund_total = sum(data[m][fund.id] for m in q_months)
			row.append(round(fund_total, 2))
			q_total += fund_total
		row.append(round(q_total, 2))
		writer.writerow(row)

	return response


def tin(request):
	"""Display TIN (Taxpayer Identification Number) report."""
	return render(request, 'reports_app/reports/allocations/tin.html')


__all__ = [
	'tin',
	'fund_report',
	'mooe_report',
	'nc_report',
	'expense_report',
	'download_mooe',
	'download_fund',
]
