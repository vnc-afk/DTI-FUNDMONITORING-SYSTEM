from django.apps import AppConfig


class BankStatementAppConfig(AppConfig):
    name = "bank_statement_app"

    def ready(self):
        import bank_statement_app.signals  # noqa
