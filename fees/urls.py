from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import (
    FeeCategoryViewSet, FeeTypeViewSet, FeeMasterViewSet, StudentFeeViewSet,
    DiscountViewSet, TransactionViewSet
)

router = DefaultRouter()
router.register(r'api/feecategories', FeeCategoryViewSet)
router.register(r'api/feetypes', FeeTypeViewSet)
router.register(r'api/feemasters', FeeMasterViewSet)
router.register(r'api/studentfees', StudentFeeViewSet)
router.register(r'api/discounts', DiscountViewSet)
router.register(r'api/transactions', TransactionViewSet)

urlpatterns = [
    path('', views.FeeCategoryListView.as_view(), name='fee-category-list'),
    path('add/', views.FeeCategoryCreateView.as_view(), name='fee-category-add'),
    path('<int:pk>/edit/', views.FeeCategoryUpdateView.as_view(), name='fee-category-edit'),
    path('<int:pk>/delete/', views.FeeCategoryDeleteView.as_view(), name='fee-category-delete'),
    path('', include(router.urls)),
]
