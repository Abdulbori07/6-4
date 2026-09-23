from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import AdminOnlyView, CustomTokenObtainPairView, GoogleAuthView, LogoutView, ProfileStatsView, UserOnlyView

urlpatterns = [
    path('v1/auth/google/', GoogleAuthView.as_view(), name='google-auth'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token-obtain-pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/stats/', ProfileStatsView.as_view(), name='profile-stats'),
    path('admin-only/', AdminOnlyView.as_view(), name='admin-only'),
    path('user-only/', UserOnlyView.as_view(), name='user-only'),
]

