from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers


class GoogleAuthSerializer(serializers.Serializer):
    code = serializers.CharField(trim_whitespace=True, allow_blank=False)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adds the authenticated user's data to the standard JWT token response."""

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user
        data['user'] = {
            'id': user.id,
            'email': user.email,
            'username': user.username,
            'role': user.role,
        }
        return data
