from django.contrib import admin
from .models import Student, Category, SchoolClass, Section

admin.site.register(Student)
admin.site.register(Category)
admin.site.register(SchoolClass)
admin.site.register(Section)

# Register your models here.
