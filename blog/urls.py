from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import PostViewSet
from .comment_views import CommentDetailView

router = DefaultRouter()
router.register('posts', PostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls)),

    path(
        'comments/<int:pk>/',
        CommentDetailView.as_view(),
        name='comment-detail'
    ),
]
