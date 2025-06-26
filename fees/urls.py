from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import (
    FeeCategoryViewSet, 
    FeeStructureViewSet, 
    FeePaymentViewSet
)

router = DefaultRouter()
router.register(r'categories', FeeCategoryViewSet, basename='feecategory')
router.register(r'structures', FeeStructureViewSet, basename='feestructure')
router.register(r'payments', FeePaymentViewSet, basename='feepayment')

urlpatterns = [
    # API URLs - Primary functionality
    path('', include(router.urls)),
] 