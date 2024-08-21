from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views
from django.urls.conf import include

router = DefaultRouter()
router.register(r'profiles', views.ProfileViewSet, basename='profiles')

urlpatterns = [
    path('register/', views.register, name='register'),
    path('', include(router.urls)),
]