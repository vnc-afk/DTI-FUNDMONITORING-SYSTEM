from rest_framework import viewsets
from rest_framework.response import Response

from user_app.permissions import IsAuthenticatedReadOnlyOrStaff

from .models import (
    BreakdownCategory,
    District,
    Division,
    ExpenseCategory,
    ExpenseObject,
    FundSource,
    FundSourceBreakdown,
    NegosyoCenter,
    PurchaseType,
    Staff,
    Supplier,
    TaxTable,
)
from .serializers import (
    BreakdownCategorySerializer,
    DistrictSerializer,
    DivisionSerializer,
    ExpenseCategorySerializer,
    ExpenseObjectSerializer,
    FundSourceBreakdownSerializer,
    FundSourceSerializer,
    NegosyoCenterSerializer,
    PurchaseTypeSerializer,
    StaffSerializer,
    SupplierSerializer,
    TaxTableSerializer,
)


class DivisionViewSet(viewsets.ModelViewSet):
    queryset = Division.objects.all().order_by("name")
    serializer_class = DivisionSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class StaffViewSet(viewsets.ModelViewSet):
    queryset = (
        Staff.objects.select_related("division")
        .all()
        .order_by("last_name", "first_name")
    )
    serializer_class = StaffSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class SupplierViewSet(viewsets.ModelViewSet):
    from rest_framework import filters
    from user_app.pagination import UserPreferencePageNumberPagination

    queryset = Supplier.objects.all().order_by("supplier")
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]
    pagination_class = UserPreferencePageNumberPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ["supplier", "tin", "propprietor", "contact_number"]

    def get_queryset(self):
        queryset = super().get_queryset()
        vat_status = (self.request.query_params.get("vat_status") or "").strip()
        if vat_status in {"V", "NV"}:
            queryset = queryset.filter(vat_status=vat_status)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        vat_count = queryset.filter(vat_status="V").count()
        non_vat_count = queryset.filter(vat_status="NV").count()

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data["vat_count"] = vat_count
            response.data["non_vat_count"] = non_vat_count
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "results": serializer.data,
                "count": len(serializer.data),
                "vat_count": vat_count,
                "non_vat_count": non_vat_count,
            }
        )


class FundSourceViewSet(viewsets.ModelViewSet):
    queryset = FundSource.objects.all().order_by("name")
    serializer_class = FundSourceSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class BreakdownCategoryViewSet(viewsets.ModelViewSet):
    queryset = BreakdownCategory.objects.all().order_by("order", "code")
    serializer_class = BreakdownCategorySerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class FundSourceBreakdownViewSet(viewsets.ModelViewSet):
    queryset = (
        FundSourceBreakdown.objects.select_related("fund_source", "category")
        .all()
        .order_by("fund_source__name", "category__order", "category__code")
    )
    serializer_class = FundSourceBreakdownSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class ExpenseObjectViewSet(viewsets.ModelViewSet):
    queryset = ExpenseObject.objects.all().order_by("code")
    serializer_class = ExpenseObjectSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class ExpenseCategoryViewSet(viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all().order_by("name")
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class DistrictViewSet(viewsets.ModelViewSet):
    queryset = District.objects.all().order_by("order", "name")
    serializer_class = DistrictSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class NegosyoCenterViewSet(viewsets.ModelViewSet):
    queryset = (
        NegosyoCenter.objects.select_related("district")
        .all()
        .order_by("district__order", "district__name", "name")
    )
    serializer_class = NegosyoCenterSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class PurchaseTypeViewSet(viewsets.ModelViewSet):
    queryset = PurchaseType.objects.all().order_by("name")
    serializer_class = PurchaseTypeSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


class TaxTableViewSet(viewsets.ModelViewSet):
    queryset = (
        TaxTable.objects.select_related("purchase_type")
        .all()
        .order_by("purchase_type__name")
    )
    serializer_class = TaxTableSerializer
    permission_classes = [IsAuthenticatedReadOnlyOrStaff]


__all__ = [
    "DivisionViewSet",
    "StaffViewSet",
    "SupplierViewSet",
    "FundSourceViewSet",
    "BreakdownCategoryViewSet",
    "FundSourceBreakdownViewSet",
    "ExpenseObjectViewSet",
    "ExpenseCategoryViewSet",
    "DistrictViewSet",
    "NegosyoCenterViewSet",
    "PurchaseTypeViewSet",
    "TaxTableViewSet",
]
