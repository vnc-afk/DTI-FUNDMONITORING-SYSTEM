from rest_framework import serializers

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


class DivisionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Division
        fields = "__all__"


class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = "__all__"


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = "__all__"


class FundSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FundSource
        fields = "__all__"


class BreakdownCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BreakdownCategory
        fields = "__all__"


class FundSourceBreakdownSerializer(serializers.ModelSerializer):
    category_code = serializers.SerializerMethodField()

    class Meta:
        model = FundSourceBreakdown
        fields = [
            "id",
            "fund_source",
            "category",
            "category_code",
            "budget_amount",
            "created_at",
            "updated_at",
        ]

    def get_category_code(self, obj):
        """Get the category code from the related category object"""
        return obj.category.code if obj.category else None


class ExpenseObjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseObject
        fields = "__all__"


class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = "__all__"


class DistrictSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = "__all__"


class NegosyoCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = NegosyoCenter
        fields = "__all__"


class PurchaseTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseType
        fields = "__all__"


class TaxTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaxTable
        fields = "__all__"


__all__ = [
    "DivisionSerializer",
    "StaffSerializer",
    "SupplierSerializer",
    "FundSourceSerializer",
    "BreakdownCategorySerializer",
    "FundSourceBreakdownSerializer",
    "ExpenseObjectSerializer",
    "ExpenseCategorySerializer",
    "DistrictSerializer",
    "NegosyoCenterSerializer",
    "PurchaseTypeSerializer",
    "TaxTableSerializer",
]
