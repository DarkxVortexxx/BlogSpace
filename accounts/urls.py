from django.urls import path
from .views import (
    csrf_token,
    RegisterView,
    LoginView,
    LogoutView,
    CurrentUserView,
    ProfileView
)

urlpatterns = [
    path('csrf/', csrf_token),
    path('register/', RegisterView.as_view()),
    path('login/', LoginView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('me/', CurrentUserView.as_view()),
    path('profile/', ProfileView.as_view(), name='profile'),
]
