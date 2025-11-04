from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    RegistrationAPIView,
    ResetPasswordAPIView,
    VerifyEmailAPIView,
    SetPasswordAPIView,
    UserLoginView,
    UserProfileView,
    ChangePasswordView,
    LogoutView,
    ForgotPasswordView,
    PasswordResetConfirmView,
    ConfirmNewEmailView
)

urlpatterns = [
    path('signup/', RegistrationAPIView.as_view(), name='signup'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='verify-email'),
    path('set-password/', SetPasswordAPIView.as_view(), name='set-password'),
    path('signin/', UserLoginView.as_view(), name='signin'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path("logout/", LogoutView.as_view(), name="logout"),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('reset-password/', PasswordResetConfirmView.as_view(), name='reset-password'),
    path('confirm-new-email/', ConfirmNewEmailView.as_view(), name='confirm-new-email'),
]