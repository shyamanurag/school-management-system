from django.contrib import admin
from .models import Book, LibraryMember, BookIssue

admin.site.register(Book)
admin.site.register(LibraryMember)
admin.site.register(BookIssue)

# Register your models here.
