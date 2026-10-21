from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .api_views import (AdminUserDetailView, AdminUserListCreateView, LoginView,
                        LogoutView, MeView, RegisterView)

urlpatterns = [
    path("login/", LoginView.as_view(), name="api-login"),
    path("register/", RegisterView.as_view(), name="api-register"),
    path("refresh/", TokenRefreshView.as_view(), name="api-refresh"),
    path("logout/", LogoutView.as_view(), name="api-logout"),
    path("me/", MeView.as_view(), name="api-me"),
    path("admin/users/", AdminUserListCreateView.as_view(), name="api-admin-users"),
    path("admin/users/<int:pk>/", AdminUserDetailView.as_view(), name="api-admin-user-detail"),
]
