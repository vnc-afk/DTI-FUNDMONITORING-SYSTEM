from rest_framework import serializers


class ReportSummarySerializer(serializers.Serializer):
    report = serializers.CharField()
    total_records = serializers.IntegerField()
    total_amount = serializers.FloatField()


class ReportCatalogSerializer(serializers.Serializer):
    code = serializers.CharField()
    title = serializers.CharField()
    endpoint = serializers.CharField()


__all__ = [
    "ReportSummarySerializer",
    "ReportCatalogSerializer",
]
