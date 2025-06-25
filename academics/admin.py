from django.contrib import admin
from .models import Subject, Exam, Grade, Timetable

admin.site.register(Subject)
admin.site.register(Exam)
admin.site.register(Grade)
admin.site.register(Timetable)

# Register your models here.
