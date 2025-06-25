from django.contrib import admin
from .models import ItemCategory, Item, ItemStock, ItemIssue

admin.site.register(ItemCategory)
admin.site.register(Item)
admin.site.register(ItemStock)
admin.site.register(ItemIssue)

# Register your models here.
