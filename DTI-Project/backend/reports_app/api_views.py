from decimal import Decimal

from django.db.models import Sum
from django.utils.timezone import now
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from data_management_app.models import (
    BreakdownCategory,
    District,
    ExpenseCategory,
    ExpenseObject,
    FundSource,
    FundSourceBreakdown,
)
from mater_fundmonitor_app.models import MasterFundMonitoring

from .serializers import ReportCatalogSerializer, ReportSummarySerializer


class ReportsCatalogAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        payload = [
            {
                "code": "expense",
                "title": "Expense Report",
                "endpoint": "/api/reports-app/expense/",
            },
            {
                "code": "mooe",
                "title": "MOOE Report",
                "endpoint": "/api/reports-app/mooe/",
            },
            {
                "code": "nc",
                "title": "Negosyo Center Report",
                "endpoint": "/api/reports-app/nc/",
            },
            {
                "code": "fund",
                "title": "Fund Report",
                "endpoint": "/api/reports-app/fund/",
            },
            {"code": "tin", "title": "TIN Report", "endpoint": "/api/reports-app/tin/"},
        ]
        serializer = ReportCatalogSerializer(payload, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class BaseMonitoringSummaryAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    report_code = "report"

    def get(self, request):
        year = request.query_params.get("year")
        queryset = MasterFundMonitoring.objects.all()
        if year and year.isdigit():
            queryset = queryset.filter(date__year=int(year))

        total_amount = queryset.aggregate(total=Sum("payments"))["total"] or 0
        payload = {
            "report": self.report_code,
            "total_records": queryset.count(),
            "total_amount": float(total_amount),
        }
        serializer = ReportSummarySerializer(payload)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ExpenseReportAPIView(BaseMonitoringSummaryAPIView):
    report_code = "expense"

    def get(self, request):
        group_by = request.query_params.get("group_by", "classification")
        is_object_grouping = group_by == "object"

        if is_object_grouping:
            groups = ExpenseObject.objects.filter(is_active=True).values(
                "id", "code", "name", "color"
            )
            group_fk = "account_title_id"
            group_label = "Object of Expense"
            search_placeholder = "Search object of expense..."
        else:
            groups = ExpenseCategory.objects.filter(is_active=True).values(
                "id", "name", "color"
            )
            group_fk = "expense_classification_id"
            group_label = "Expense Category"
            search_placeholder = "Search expense category..."

        current_year = now().year
        expense_data = []

        for group in groups:
            filter_kwargs = {group_fk: group["id"], "date__year": current_year}
            expenses = MasterFundMonitoring.objects.filter(**filter_kwargs).values_list(
                "date", "payments"
            )

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
                    "name": (
                        f"({group['code']}) {group['name']}"
                        if is_object_grouping
                        else group["name"]
                    ),
                    "color": group["color"],
                    "q1": [float(value) for value in q1],
                    "q2": [float(value) for value in q2],
                    "q3": [float(value) for value in q3],
                    "q4": [float(value) for value in q4],
                }
            )

        return Response(
            {
                "report": "expense",
                "current_year": current_year,
                "group_by": "object" if is_object_grouping else "classification",
                "group_label": group_label,
                "search_placeholder": search_placeholder,
                "expense_data": expense_data,
            },
            status=status.HTTP_200_OK,
        )


class MooeReportAPIView(BaseMonitoringSummaryAPIView):
    report_code = "mooe"

    def get(self, request):
        month_names = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        categories = BreakdownCategory.objects.filter(is_active=True).order_by(
            "order", "code"
        )
        category_codes = ["OO1", "OO2", "OO3", "4.1A", "4.1B", "4.2"]

        budget_data = {}
        grand_total_budget = Decimal(0)
        grand_total_disbursed = Decimal(0)

        for category in categories:
            annual_budget = FundSourceBreakdown.objects.filter(
                category=category
            ).aggregate(total=Sum("budget_amount"))["total"] or Decimal(0)
            total_disbursed = MasterFundMonitoring.objects.filter(
                mooe=category.code
            ).aggregate(total=Sum("payments"))["total"] or Decimal(0)

            current_balance = annual_budget - total_disbursed
            bur = (
                (total_disbursed / annual_budget) * 100
                if annual_budget > 0
                else Decimal(0)
            )

            budget_data[category.code] = {
                "name": category.name,
                "annual_budget": float(annual_budget),
                "total_disbursed": float(total_disbursed),
                "current_balance": float(current_balance),
                "bur": float(bur),
            }

            grand_total_budget += annual_budget
            grand_total_disbursed += total_disbursed

        grand_balance = grand_total_budget - grand_total_disbursed
        grand_bur = (
            (grand_total_disbursed / grand_total_budget) * 100
            if grand_total_budget > 0
            else Decimal(0)
        )

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
                monthly_payments = MasterFundMonitoring.objects.filter(
                    mooe=code,
                    date__month=month_num,
                    date__year=current_year,
                ).aggregate(total=Sum("payments"))["total"] or Decimal(0)
                disbursement_data[month_num][code] = float(monthly_payments)

                monthly_downloads = MasterFundMonitoring.objects.filter(
                    mooe=code,
                    date__month=month_num,
                    date__year=current_year,
                ).aggregate(total=Sum("downloads"))["total"] or Decimal(0)
                downloads_data[month_num][code] = float(monthly_downloads)

        disbursement_breakdown = []
        downloads_breakdown = []

        def calc_row_total(data_dict, codes):
            return sum(data_dict.get(code, 0) for code in codes)

        for month_num in range(1, 13):
            row_total = calc_row_total(disbursement_data[month_num], category_codes)
            disbursement_breakdown.append(
                {
                    "month": month_names[month_num - 1],
                    "month_num": month_num,
                    "data": disbursement_data[month_num],
                    "total": row_total,
                    "quarter": None,
                }
            )

            row_total = calc_row_total(downloads_data[month_num], category_codes)
            downloads_breakdown.append(
                {
                    "month": month_names[month_num - 1],
                    "month_num": month_num,
                    "data": downloads_data[month_num],
                    "total": row_total,
                    "quarter": None,
                }
            )

        return Response(
            {
                "report": "mooe",
                "current_year": current_year,
                "categoryCodes": category_codes,
                "budgetData": budget_data,
                "disbursementBreakdown": disbursement_breakdown,
                "downloadsBreakdown": downloads_breakdown,
                "grandTotalBudget": float(grand_total_budget),
                "grandTotalDisbursed": float(grand_total_disbursed),
                "grandBalance": float(grand_balance),
                "grandBur": float(grand_bur),
            },
            status=status.HTTP_200_OK,
        )


class NcReportAPIView(BaseMonitoringSummaryAPIView):
    report_code = "nc"

    def get(self, request):
        current_year = now().year
        districts = District.objects.prefetch_related("negosyo_centers").order_by(
            "order", "name"
        )

        month_names = [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

        districts_data = []
        total_disbursement = 0.0
        total_downloads = 0.0

        for district in districts:
            negosyo_centers = district.negosyo_centers.filter(is_active=True).order_by(
                "name"
            )
            if not negosyo_centers.exists():
                continue

            nc_ids = list(negosyo_centers.values_list("id", flat=True))
            transactions = MasterFundMonitoring.objects.filter(
                nc_id__in=nc_ids,
                date__year=current_year,
            ).order_by("nc__name", "date")

            monthly_data = {month: {} for month in range(1, 13)}
            for nc in negosyo_centers:
                for month_num in range(1, 13):
                    monthly_data[month_num][str(nc.id)] = 0.0

            for transaction in transactions:
                month_num = transaction.date.month
                nc_id = str(transaction.nc_id)
                payment = float(transaction.payments or 0)
                monthly_data[month_num][nc_id] += payment
                total_disbursement += payment
                total_downloads += float(transaction.downloads or 0)

            quarters = []
            quarter_configs = [
                {"months": [1, 2, 3], "label": "Q1", "range": "January - March"},
                {"months": [4, 5, 6], "label": "Q2", "range": "April - June"},
                {"months": [7, 8, 9], "label": "Q3", "range": "July - September"},
                {"months": [10, 11, 12], "label": "Q4", "range": "October - December"},
            ]

            for quarter_config in quarter_configs:
                quarter_months = []
                quarter_total = 0

                for month_num in quarter_config["months"]:
                    month_row = {
                        "name": month_names[month_num - 1],
                        "month_num": month_num,
                        "nc_data": {},
                        "month_total": 0,
                    }

                    for nc in negosyo_centers:
                        amount = monthly_data[month_num].get(str(nc.id), 0.0)
                        month_row["nc_data"][str(nc.id)] = amount
                        month_row["month_total"] += amount
                        quarter_total += amount

                    quarter_months.append(month_row)

                quarters.append(
                    {
                        "label": quarter_config["label"],
                        "range": quarter_config["range"],
                        "months": quarter_months,
                        "total": quarter_total,
                    }
                )

            districts_data.append(
                {
                    "name": district.name,
                    "order": district.order,
                    "negosyo_centers": [
                        {"id": str(nc.id), "name": nc.name} for nc in negosyo_centers
                    ],
                    "quarters": quarters,
                    "district_total": sum(quarter["total"] for quarter in quarters),
                }
            )

        annual_budget = FundSource.objects.filter(
            name__icontains="negosyo center"
        ).aggregate(total=Sum("annual_budget"))["total"] or Decimal(0)
        annual_budget = float(annual_budget)
        current_balance = annual_budget - total_disbursement
        bur_rate = (
            (total_disbursement / annual_budget * 100) if annual_budget > 0 else 0
        )

        return Response(
            {
                "report": "nc",
                "current_year": current_year,
                "districts": districts_data,
                "totalDisbursement": total_disbursement,
                "totalDownloads": total_downloads,
                "annualBudget": annual_budget,
                "currentBalance": current_balance,
                "burRate": bur_rate,
            },
            status=status.HTTP_200_OK,
        )


class FundReportAPIView(BaseMonitoringSummaryAPIView):
    report_code = "fund"

    def get(self, request):
        month_names = [
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        ]

        fund_sources = FundSource.objects.filter(annual_budget__gt=0).order_by("name")
        fund_sources_with_data = FundSource.objects.filter(
            id__in=MasterFundMonitoring.objects.values_list(
                "fund_source_id", flat=True
            ).distinct()
        ).order_by("name")

        all_fund_ids = set([fund.id for fund in fund_sources]) | set(
            [fund.id for fund in fund_sources_with_data]
        )
        fund_sources = FundSource.objects.filter(id__in=all_fund_ids).order_by("name")
        fund_codes = [str(fund.id) for fund in fund_sources]
        current_year = now().year

        budget_data = {}
        grand_total_budget = 0
        grand_total_disbursed = 0
        grand_total_downloads = 0

        for fund in fund_sources:
            annual_budget = fund.annual_budget or 0
            total_disbursed = (
                MasterFundMonitoring.objects.filter(fund_source=fund).aggregate(
                    total=Sum("payments")
                )["total"]
                or 0
            )
            total_downloads = (
                MasterFundMonitoring.objects.filter(fund_source=fund).aggregate(
                    total=Sum("downloads")
                )["total"]
                or 0
            )

            current_balance = float(annual_budget) - float(total_disbursed)
            bur_percent = (
                (float(total_disbursed) / float(annual_budget) * 100)
                if annual_budget > 0
                else 0
            )

            budget_data[str(fund.id)] = {
                "annual_budget": float(annual_budget),
                "total_disbursed": float(total_disbursed),
                "total_downloads": float(total_downloads),
                "current_balance": current_balance,
                "bur_percent": bur_percent,
            }

            grand_total_budget += float(annual_budget)
            grand_total_disbursed += float(total_disbursed)
            grand_total_downloads += float(total_downloads)

        grand_total_balance = grand_total_budget - grand_total_disbursed
        grand_total_bur = (
            (grand_total_disbursed / grand_total_budget * 100)
            if grand_total_budget > 0
            else 0
        )

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
                    ).aggregate(total=Sum("payments"))["total"]
                    or 0
                )

                month_downloads = (
                    MasterFundMonitoring.objects.filter(
                        fund_source=fund,
                        date__month=month_num,
                        date__year=current_year,
                    ).aggregate(total=Sum("downloads"))["total"]
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
                    "month": month_names[month_num - 1],
                    "month_num": month_num,
                    "data": disbursement_data[month_num],
                    "total": row_total,
                    "quarter": None,
                }
            )

            row_total = calc_row_total(downloads_data[month_num], fund_codes)
            downloads_breakdown.append(
                {
                    "month": month_names[month_num - 1],
                    "month_num": month_num,
                    "data": downloads_data[month_num],
                    "total": row_total,
                    "quarter": None,
                }
            )

        return Response(
            {
                "report": "fund",
                "current_year": current_year,
                "funds": [{"id": str(f.id), "name": f.name} for f in fund_sources],
                "budgetData": budget_data,
                "disbursementBreakdown": disbursement_breakdown,
                "downloadsBreakdown": downloads_breakdown,
                "grandTotalBudget": grand_total_budget,
                "grandTotalDisbursed": grand_total_disbursed,
                "grandTotalDownloads": grand_total_downloads,
                "grandTotalBalance": grand_total_balance,
                "grandTotalBur": grand_total_bur,
            },
            status=status.HTTP_200_OK,
        )


class TinReportAPIView(BaseMonitoringSummaryAPIView):
    report_code = "tin"


__all__ = [
    "ReportsCatalogAPIView",
    "ExpenseReportAPIView",
    "MooeReportAPIView",
    "NcReportAPIView",
    "FundReportAPIView",
    "TinReportAPIView",
]
