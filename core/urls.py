from django.urls import path
from . import simple_views

app_name = 'core'

urlpatterns = [
    path('', simple_views.dashboard, name='dashboard'),
]
