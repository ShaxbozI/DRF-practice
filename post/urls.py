from django.urls import path
from .views import PostListApiView, PostCreateView, PostRetriveUpdateDestroyView, PostCommentListView, PostCommentCreateView, PostLikeListView

urlpatterns = [
    path('posts/', PostListApiView.as_view()),
    path('/create/', PostCreateView.as_view()),
    path('/<uuid:pk>/', PostRetriveUpdateDestroyView.as_view()),
    path('/<uuid:pk>/comments/', PostCommentListView.as_view()),
    path('/<uuid:pk>/comments/create/', PostCommentCreateView.as_view()),
    path('/<uuid:pk>/likes/', PostLikeListView.as_view()),
]