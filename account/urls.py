from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    PasswordChangeView,
    PasswordResetView,
    PasswordResetTokenVerificationView,
    UserReadOnlyViewSet,
    UserRegistrationView,
)


read_only_user_router = DefaultRouter()
read_only_user_router.register("", UserReadOnlyViewSet)

urlpatterns = [
    path("register/", UserRegistrationView.as_view(), name="user-register"),
    path("user/", include(read_only_user_router.urls)),
    path(
        "user/search",
        UserReadOnlyViewSet.as_view({"get": "search"}),
        name="user-search",
    ),
]

# Password Reset
urlpatterns += [
    path("password/change/", PasswordChangeView.as_view(), name="password-change"),
    path("password/reset/", PasswordResetView.as_view(), name="password-reset"),
    path(
        "password/reset/verify/",
        PasswordResetTokenVerificationView.as_view(),
        name="password-reset-token-verification",
    ),
]

# Simple JWT Token
urlpatterns += [
    path("token/", TokenObtainPairView.as_view(), name="token-obtain-pair"),
    path("token/refresh", TokenRefreshView.as_view(), name="token-refresh"),
    path("token/verify", TokenVerifyView.as_view(), name="token-verify"),
]
