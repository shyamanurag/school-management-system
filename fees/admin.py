from django.contrib import admin
from .models import FeeCategory, FeeType, FeeMaster, StudentFee, Discount, Transaction

admin.site.register(FeeCategory)
admin.site.register(FeeType)
admin.site.register(FeeMaster)
admin.site.register(StudentFee)
admin.site.register(Discount)
admin.site.register(Transaction)

# Register your models here.
