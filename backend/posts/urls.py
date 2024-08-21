from rest_framework.routers import DefaultRouter
from django.urls.conf import path

from django.urls.conf import include
from . import views
from .views import CategoryView

router = DefaultRouter()

router.register(r'posts', views.PostViewSet, basename='posts')
router.register(r'comments', views.CommentView, basename='comment')

urlpatterns = [
    path('', include(router.urls)),
    path('categories/', CategoryView.as_view(), name='category-list'),
    path('categories/<int:category_id>/', CategoryView.as_view(), name='category-detail'),
]