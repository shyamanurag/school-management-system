from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import ItemCategoryViewSet, ItemViewSet, ItemStockViewSet, ItemIssueViewSet

router = DefaultRouter()
router.register(r'api/itemcategories', ItemCategoryViewSet)
router.register(r'api/items', ItemViewSet)
router.register(r'api/itemstocks', ItemStockViewSet)
router.register(r'api/itemissues', ItemIssueViewSet)

urlpatterns = [
    path('', views.ItemListView.as_view(), name='item-list'),
    path('add/', views.ItemCreateView.as_view(), name='item-add'),
    path('<int:pk>/edit/', views.ItemUpdateView.as_view(), name='item-edit'),
    path('<int:pk>/delete/', views.ItemDeleteView.as_view(), name='item-delete'),
    path('', include(router.urls)),
]
