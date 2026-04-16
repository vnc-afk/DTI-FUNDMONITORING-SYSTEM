from rest_framework import serializers

from .models import BankAccount, BankStatement


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "id",
            "name",
            "account_number",
            "opening_balance",
            "is_active",
            "created_at",
            "updated_at",
        ]


class BankStatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankStatement
        fields = [
            "id",
            "date",
            "description",
            "check_number",
            "debit",
            "credit",
            "balance",
            "status",
            "is_archived",
            "archived_at",
            "archived_by",
            "archive_reason",
            "created_at",
            "updated_at",
        ]


__all__ = [
    "BankAccountSerializer",
    "BankStatementSerializer",
]
