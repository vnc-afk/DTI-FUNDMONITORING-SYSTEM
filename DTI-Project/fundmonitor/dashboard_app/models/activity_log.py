from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse


class ActivityLog(models.Model):
    """Model to track all user activities and system changes"""
    
    ACTION_CHOICES = [
        ('CREATE', 'Created'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
        ('VIEW', 'Viewed'),
        ('DOWNLOAD', 'Downloaded'),
        ('IMPORT', 'Imported'),
        ('LOGIN', 'Logged In'),
        ('LOGOUT', 'Logged Out'),
        ('PASSWORD_CHANGE', 'Changed Password'),
        ('SETTINGS_CHANGE', 'Changed Settings'),
        ('BULK_DELETE', 'Bulk Deleted'),
        ('STATUS_CHANGE', 'Changed Status'),
    ]
    
    # User and action info
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='activity_logs')
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    
    # What was affected
    model_name = models.CharField(max_length=100)  # e.g., 'BankStatement', 'Supplier'
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)  # String representation of the object
    
    # Details about the change
    description = models.TextField(blank=True)
    
    # Previous and new values (for tracking changes)
    changed_fields = models.JSONField(default=dict, blank=True)  # e.g., {'field_name': {'old': value, 'new': value}}
    
    # Meta information
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Status
    is_sensitive = models.BooleanField(default=False)  # Mark sensitive operations
    
    class Meta:
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['model_name', 'object_id']),
        ]
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} {self.model_name} ({self.timestamp.strftime('%Y-%m-%d %H:%M')})"
    
    def get_formatted_timestamp(self):
        """Return human-readable timestamp"""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    
    def get_time_ago(self):
        """Return time ago in human-readable format"""
        from django.utils.timezone import now
        from django.utils.timesince import timesince
        return timesince(self.timestamp, now())
    
    def get_changed_fields_display(self):
        """Format changed fields for display"""
        if not self.changed_fields:
            return "No field changes recorded"
        
        changes = []
        for field, values in self.changed_fields.items():
            if isinstance(values, dict) and 'old' in values and 'new' in values:
                changes.append(f"{field}: '{values['old']}' → '{values['new']}'")
        
        return ', '.join(changes) if changes else "Field data not available"
    
    @property
    def is_admin_action(self):
        """Check if action was performed by admin"""
        return self.user.is_staff
    
    @property
    def is_staff_action(self):
        """Check if action was performed by staff member"""
        return self.user.is_staff or self.user.groups.filter(name='Staff').exists()
