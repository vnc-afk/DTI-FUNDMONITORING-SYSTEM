from django.apps import AppConfig


class DashboardAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'dashboard_app'
    
    def ready(self):
        """Import signals when app is ready"""
        import dashboard_app.signals  # noqa
