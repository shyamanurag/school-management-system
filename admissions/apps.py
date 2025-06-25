from django.apps import AppConfig


class AdmissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'admissions'
    verbose_name = 'Admissions Management'
    
    def ready(self):
        # import admissions.signals  # noqa
        pass 