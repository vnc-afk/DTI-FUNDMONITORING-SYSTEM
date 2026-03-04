"""Expenses Report View - Aggregated expenses by account and month"""
import json
from django.views.generic import TemplateView
from decimal import Decimal
from datetime import datetime

from dashboard_app.models import MasterFundMonitoring, ExpenseObject


class ExpensesReportView(TemplateView):
    """Generate expenses report aggregated by ExpenseObject and month"""

    template_name = 'funding/reports/expenses_report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        current_year = datetime.now().year
        year = int(self.request.GET.get('year', current_year))
        years = [current_year - i for i in range(5)]

        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']

        # ── 1. Seed report_data from ALL active ExpenseObjects ──────────────
        # This ensures every expense object appears in the report,
        # even if it has no transactions for the selected year.
        report_data = {}
        for obj in ExpenseObject.objects.filter(is_active=True).order_by('code'):
            account_key = f"({obj.code}) {obj.name}"
            report_data[account_key] = {
                'code': obj.code,
                'name': obj.name,
                'color': obj.color,
                'monthly': [Decimal('0.00')] * 12,
                'total': Decimal('0.00'),
            }

        # ── 2. Fill in transaction amounts ───────────────────────────────────
        transactions = (
            MasterFundMonitoring.objects
            .filter(date__year=year, account_title__isnull=False)
            .select_related('account_title')
            .order_by('date')
        )

        for tx in transactions:
            obj = tx.account_title
            account_key = f"({obj.code}) {obj.name}"
            month = tx.date.month
            amount = tx.payments or Decimal('0.00')

            # account_key will always exist because we seeded from ExpenseObject,
            # but guard just in case a deactivated object slips through
            if account_key not in report_data:
                report_data[account_key] = {
                    'code': obj.code,
                    'name': obj.name,
                    'color': obj.color or '#64748b',
                    'monthly': [Decimal('0.00')] * 12,
                    'total': Decimal('0.00'),
                }

            report_data[account_key]['monthly'][month - 1] += amount
            report_data[account_key]['total'] += amount

        # ── 3. Build rows ────────────────────────────────────────────────────
        grand_total = sum(d['total'] for d in report_data.values())

        rows = []
        for account_key, data in report_data.items():
            monthly_floats = [float(v) for v in data['monthly']]
            row = {
                'account': account_key,
                'code': data['code'],
                'name': data['name'],
                'color': data['color'],
                'total': float(data['total']),
                'percentage': float(
                    (data['total'] / grand_total * 100)
                    if grand_total > 0 else Decimal('0.00')
                ),
                'monthly': monthly_floats,
                'q1': sum(monthly_floats[0:3]),
                'q2': sum(monthly_floats[3:6]),
                'q3': sum(monthly_floats[6:9]),
                'q4': sum(monthly_floats[9:12]),
            }
            rows.append(row)

        # ── 4. Build expense_json for JS rendering ───────────────────────────
        expense_json = [
            {
                "name": r["account"],
                "color": r["color"],
                "q1": r["monthly"][0:3],
                "q2": r["monthly"][3:6],
                "q3": r["monthly"][6:9],
                "q4": r["monthly"][9:12],
            }
            for r in rows
        ]

        context.update({
            'year': year,
            'years': years,
            'rows': rows,
            'grand_total': float(grand_total),
            'months': months,
            'expense_json': json.dumps(expense_json),
        })

        return context