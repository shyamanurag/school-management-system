from django.contrib import admin
from .models import Hostel, RoomType, HostelRoom, HostelAssignment

admin.site.register(Hostel)
admin.site.register(RoomType)
admin.site.register(HostelRoom)
admin.site.register(HostelAssignment)

# Register your models here.
