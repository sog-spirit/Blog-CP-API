from django.urls import path
from .views.user_views import UserLogin, UserLogout, UserRegister, UserStatus
from .views.post_views import GetPosts, GetPostDetail, PostAPIView
from .views.comment_views import CommentAPIView, CommentDetailAPIView

urlpatterns = [
    path('user/register', UserRegister.as_view()),
    path('user/login', UserLogin.as_view()),
    path('user/logout', UserLogout.as_view()),
    path('user/status', UserStatus.as_view()),
    path('posts', GetPosts.as_view()),
    path('post', PostAPIView.as_view()),
    path('post/detail', GetPostDetail.as_view()),
    path('comment', CommentAPIView.as_view()),
    path('comment/detail', CommentDetailAPIView.as_view()),
]