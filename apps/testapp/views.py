from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from .permissions import IsAdminOnly, IsUserOnly
from .serializers import CustomTokenObtainPairSerializer, GoogleAuthSerializer
from .services import get_google_access_token, get_google_user_info
from django.contrib.auth import get_user_model
from django.utils.text import slugify


class GoogleAuthView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = GoogleAuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        access_token = get_google_access_token(serializer.validated_data['code'])
        profile = get_google_user_info(access_token)
        User = get_user_model()
        email = profile['email'].strip().lower()
        user = User.objects.filter(email__iexact=email).first()
        is_new_user = user is None

        if is_new_user:
            username_base = slugify(email.split('@', 1)[0]) or 'user'
            username = username_base
            suffix = 1
            while User.objects.filter(username=username).exists():
                username = f'{username_base}{suffix}'
                suffix += 1
            user = User(email=email, username=username)
            user.set_unusable_password()
            user.first_name = profile.get('name', '')[:150]
            user.save()

        refresh = RefreshToken.for_user(user)
        refresh['email'] = user.email
        refresh['role'] = user.role
        return Response({
            'user': {
                'id': user.id,
                'email': user.email,
                'username': user.username,
                'name': profile.get('name') or user.get_full_name(),
                'role': user.role,
            },
            'is_new_user': is_new_user,
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_200_OK)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'detail': 'Поле refresh обязательно.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
        except Exception:
            return Response({'detail': 'Некорректный refresh токен.'}, status=status.HTTP_400_BAD_REQUEST)

        if str(token['user_id']) != str(request.user.id):
            return Response({'detail': 'Этот refresh токен принадлежит другому пользователю.'}, status=status.HTTP_403_FORBIDDEN)

        token.blacklist()

        return Response(status=status.HTTP_205_RESET_CONTENT)


class ProfileStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            'email': user.email,
            'role': user.role,
            'is_staff': user.is_staff,
            'date_joined': user.date_joined,
        })

class AdminOnlyView(APIView):
    permission_classes = [IsAdminOnly]

    def get(self, request):
        return Response({"message": "Добро пожаловать, Admin!"})

class UserOnlyView(APIView):
    permission_classes = [IsUserOnly]

    def get(self, request):
        return Response({"message": "Добро пожаловать, User!"})

    
     

