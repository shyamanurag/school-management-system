from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .api import NoticeViewSet, NotificationViewSet, MessageViewSet

router = DefaultRouter()
router.register(r'api/notices', NoticeViewSet)
router.register(r'api/notifications', NotificationViewSet)
router.register(r'api/messages', MessageViewSet)

urlpatterns = [
    path('', views.NoticeListView.as_view(), name='notice-list'),
    path('add/', views.NoticeCreateView.as_view(), name='notice-add'),
    path('<int:pk>/edit/', views.NoticeUpdateView.as_view(), name='notice-edit'),
    path('<int:pk>/delete/', views.NoticeDeleteView.as_view(), name='notice-delete'),
    path('', include(router.urls)),
]
