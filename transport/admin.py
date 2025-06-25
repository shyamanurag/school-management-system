from django.contrib import admin
from .models import Route, Vehicle, TransportAssignment

admin.site.register(Route)
admin.site.register(Vehicle)
admin.site.register(TransportAssignment)

# Register your models here.
