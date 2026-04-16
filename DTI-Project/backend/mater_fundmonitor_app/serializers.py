from rest_framework import serializers

from .models import MasterFundMonitoring


class MasterFundMonitoringSerializer(serializers.ModelSerializer):
    # Add related object names
    division_name = serializers.SerializerMethodField()
    fund_source_name = serializers.SerializerMethodField()
    nc_name = serializers.SerializerMethodField()
    payee_name = serializers.SerializerMethodField()
    purchase_type_name = serializers.SerializerMethodField()
    account_title_name = serializers.SerializerMethodField()
    expense_classification_name = serializers.SerializerMethodField()
    staff_name = serializers.SerializerMethodField()

    class Meta:
        model = MasterFundMonitoring
        fields = "__all__"

    def get_division_name(self, obj):
        return obj.division.name if obj.division else None

    def get_fund_source_name(self, obj):
        return obj.fund_source.name if obj.fund_source else None

    def get_nc_name(self, obj):
        return obj.nc.name if obj.nc else None

    def get_payee_name(self, obj):
        return obj.payee.supplier if obj.payee else None

    def get_purchase_type_name(self, obj):
        return obj.purchase_type.name if obj.purchase_type else None

    def get_account_title_name(self, obj):
        return obj.account_title.name if obj.account_title else None

    def get_expense_classification_name(self, obj):
        return obj.expense_classification.name if obj.expense_classification else None

    def get_staff_name(self, obj):
        if obj.staff:
            middle = f" {obj.staff.middle_initial}" if obj.staff.middle_initial else ""
            return f"{obj.staff.first_name}{middle} {obj.staff.last_name}"
        return None


__all__ = [
    "MasterFundMonitoringSerializer",
]
