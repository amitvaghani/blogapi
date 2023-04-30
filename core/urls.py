from django.urls import path
from .views import CreateUserView, LoginUserView, BlogPostList, BlogPostDetail,CommentList, ReplyList
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
urlpatterns = [
    path('signup/', CreateUserView.as_view(), name='signup'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(),),
    path('posts/', BlogPostList.as_view(), name='post-list'),
    path('posts/<int:pk>/', BlogPostDetail.as_view(), name='post-detail'),
    path('posts/<int:post_pk>/comments/', CommentList.as_view(), name='comment-list'),
    path('posts/<int:post_pk>/comments/<int:comment_pk>/replies/', ReplyList.as_view(), name='reply-list'),
]