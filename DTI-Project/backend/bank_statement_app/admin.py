from django.contrib import admin

from bank_statement_app.models import BankStatement


def archive_selected(modeladmin, request, queryset):
    count = queryset.count()
    for obj in queryset:
        obj.archive(user=request.user, reason="Archived via admin")
    modeladmin.message_user(request, f"{count} record(s) archived successfully.")


archive_selected.short_description = "Archive selected records"


def unarchive_selected(modeladmin, request, queryset):
    count = queryset.count()
    for obj in queryset.filter(is_archived=True):
        obj.unarchive()
    modeladmin.message_user(request, f"{count} record(s) unarchived successfully.")


unarchive_selected.short_description = "Unarchive selected records"


@admin.register(BankStatement)
class BankStatementAdmin(admin.ModelAdmin):
    list_display = ("date", "description", "debit", "credit", "balance", "is_archived")
    list_filter = ("date", "status", "is_archived")
    search_fields = ("description", "check_number")
    readonly_fields = ("archived_at", "archived_by", "created_at", "updated_at")
    actions = [archive_selected, unarchive_selected]

    fieldsets = (
        (
            "Transaction Details",
            {"fields": ("date", "description", "check_number", "status")},
        ),
        ("Amounts", {"fields": ("debit", "credit", "balance")}),
        (
            "Archive Information",
            {
                "fields": (
                    "is_archived",
                    "archived_at",
                    "archived_by",
                    "archive_reason",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Metadata",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
