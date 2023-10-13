
from .views import ChangeUserInformationView
from .serializers import SignUpSerializer
from .views import (CreateUserView, VerifyAPIView, ChangeUserPhotoView, 
LoginUserView, LoginRefreshView, LogoutUserView, ForgotPasswordView, RessetPasswordView
)
from django.urls import path

urlpatterns = [
    path('login/', LoginUserView.as_view()),
    path('login/refresh/', LoginRefreshView.as_view()),
    path('logout/', LogoutUserView.as_view()),
    path('singup/', CreateUserView.as_view()),
    path('verify/', VerifyAPIView.as_view()),
    path('change_user/', ChangeUserInformationView.as_view()),
    path('change_user-photo/', ChangeUserPhotoView.as_view()),
    path('forgot/password/', ForgotPasswordView.as_view()),
    path('resset/password/', RessetPasswordView.as_view()),
]