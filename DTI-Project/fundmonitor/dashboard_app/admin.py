from django.contrib import admin
from django.utils.html import format_html
from .models import ActivityLog, Notification

# Activity Log Management
class ActivityLogAdmin(admin.ModelAdmin):
    """Admin interface for Activity Logs"""
    list_display = ('timestamp', 'user_link', 'action_badge', 'model_name', 'object_repr_short', 'is_sensitive_badge')
    list_filter = ('action', 'timestamp', 'is_sensitive', 'model_name', 'user')
    readonly_fields = ('timestamp', 'user', 'action', 'model_name', 'object_id', 
                      'object_repr', 'changed_fields', 'ip_address', 'user_agent', 'is_sensitive')
    date_hierarchy = 'timestamp'
    search_fields = ('user__username', 'object_repr', 'description', 'model_name')
    ordering = ('-timestamp',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'ip_address', 'user_agent')
        }),
        ('Action Details', {
            'fields': ('action', 'timestamp')
        }),
        ('Model Information', {
            'fields': ('model_name', 'object_id', 'object_repr')
        }),
        ('Changes', {
            'fields': ('changed_fields', 'description'),
            'classes': ('collapse',)
        }),
        ('Sensitivity', {
            'fields': ('is_sensitive',)
        }),
    )
    
    def user_link(self, obj):
        """Display user with link"""
        return f"{obj.user.get_full_name() or obj.user.username}"
    user_link.short_description = 'User'
    
    def action_badge(self, obj):
        """Display action with color badge"""
        action_colors = {
            'CREATE': '#28a745',
            'UPDATE': '#17a2b8',
            'DELETE': '#dc3545',
            'VIEW': '#6c757d',
            'DOWNLOAD': '#ffc107',
            'IMPORT': '#007bff',
            'LOGIN': '#28a745',
            'LOGOUT': '#6c757d',
            'PASSWORD_CHANGE': '#ffc107',
            'SETTINGS_CHANGE': '#17a2b8',
            'BULK_DELETE': '#dc3545',
            'STATUS_CHANGE': '#17a2b8',
        }
        color = action_colors.get(obj.action, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Action'
    
    def object_repr_short(self, obj):
        """Truncate object representation"""
        return obj.object_repr[:50] + '...' if len(obj.object_repr) > 50 else obj.object_repr
    object_repr_short.short_description = 'Object'
    
    def is_sensitive_badge(self, obj):
        """Display sensitivity indicator"""
        if obj.is_sensitive:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px;">Sensitive</span>'
            )
        return format_html(
            '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px;">Normal</span>'
        )
    is_sensitive_badge.short_description = 'Type'


admin.site.register(ActivityLog, ActivityLogAdmin)


class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for user notifications."""
    list_display = ('created_at', 'user', 'title', 'level', 'category', 'is_read')
    list_filter = ('level', 'category', 'is_read', 'created_at')
    search_fields = ('user__username', 'title', 'message', 'event_key')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'read_at')


admin.site.register(Notification, NotificationAdmin)
