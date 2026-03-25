from django.contrib import admin

from mater_fundmonitor_app.models import MasterFundMonitoring


def archive_selected(modeladmin, request, queryset):
	count = queryset.count()
	for obj in queryset:
		obj.archive(user=request.user, reason='Archived via admin')
	modeladmin.message_user(request, f'{count} record(s) archived successfully.')


archive_selected.short_description = 'Archive selected records'


def unarchive_selected(modeladmin, request, queryset):
	count = queryset.count()
	for obj in queryset.filter(is_archived=True):
		obj.unarchive()
	modeladmin.message_user(request, f'{count} record(s) unarchived successfully.')


unarchive_selected.short_description = 'Unarchive selected records'


@admin.register(MasterFundMonitoring)
class MasterFundMonitoringAdmin(admin.ModelAdmin):
	list_display = ('date', 'payee', 'payments', 'transaction_type', 'cheque_status', 'is_archived')
	list_filter = ('date', 'transaction_type', 'cheque_status', 'is_archived')
	search_fields = ('payee__supplier', 'dv_number', 'cheque_number')
	readonly_fields = ('archived_at', 'archived_by', 'created_at', 'updated_at')
	actions = [archive_selected, unarchive_selected]

	fieldsets = (
		('Basic Information', {'fields': ('date', 'payee', 'transaction_type', 'particulars')}),
		('Amounts', {'fields': ('payments', 'downloads')}),
		('Cheque Information', {'fields': ('dv_number', 'cheque_number', 'cheque_status', 'cleared_date')}),
		(
			'Archive Information',
			{'fields': ('is_archived', 'archived_at', 'archived_by', 'archive_reason'), 'classes': ('collapse',)},
		),
		('Metadata', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
	)
