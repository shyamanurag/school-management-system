from django.apps import AppConfig


class HrConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hr'
    verbose_name = 'Human Resources & Payroll'
    
    def ready(self):
        # import hr.signals  # noqa
        pass