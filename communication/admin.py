from django.contrib import admin
from .models import Notice, Notification, Message

admin.site.register(Notice)
admin.site.register(Notification)
admin.site.register(Message)

# Register your models here.
