from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework import generics, views
from rest_framework.permissions import AllowAny
from random import randint
from django.utils import timezone
from .tasks import send_verificaation_code
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from .serializers import (
    RegistrationSerializer,
    VerifyEmailSerializer,
    SetPasswordSerializer,
    UserLoginSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    ForgotPasswordSerializer,
    PasswordResetConfirmSerializer,
    VerifyNewEmailSerializer
)

User = get_user_model()

class RegistrationAPIView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer 

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user is not None and not user.is_verified_email:
            verification_code = randint(1000, 9999)
            user.verification_code = verification_code
            user.verification_code_created_at = timezone.now()
            user.save()
            send_verificaation_code.delay(user.pk)

            return Response({
                "user": user.email,
                "status": status.HTTP_200_OK
            })

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create(
                email=serializer.validated_data['email'],
            )

            verification_code = randint(1000, 9999)
            user.verification_code = verification_code
            user.verification_code_created_at = timezone.now()
            user.save()
            send_verificaation_code.delay(user.pk)

            return Response({
                "user": user.email,
                "status": status.HTTP_201_CREATED
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ResetPasswordAPIView(generics.UpdateAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        email = request.data.get('email')
        user = User.objects.filter(email=email).first()

        if user is None:
            return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

        verification_code = randint(1000, 9999)
        user.verification_code = verification_code
        user.verification_code_created_at = timezone.now()
        user.save()

        return Response({
            "user": user.email,
            "status": status.HTTP_200_OK
        })


class VerifyEmailAPIView(generics.UpdateAPIView):
    serializer_class = VerifyEmailSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            verification_code = serializer.validated_data['verification_code']
            user = User.objects.filter(email=email).first()

            if user is None:
                return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)
            if user.verification_code != verification_code:
                return Response({"error": "Неверный код"}, status=status.HTTP_400_BAD_REQUEST)
            if user.verification_code_created_at + timezone.timedelta(minutes=5) < timezone.now():
                return Response({"error": "Код подтверждения истек. Запросите новый код и попробуйте снова"}, status=status.HTTP_400_BAD_REQUEST)

            user.is_verified_email = True
            user.verification_code = None
            user.save()

            return Response({"status": status.HTTP_200_OK, "user": user.email})

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SetPasswordAPIView(generics.UpdateAPIView):
    serializer_class = SetPasswordSerializer
    permission_classes = [AllowAny]

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            name = serializer.validated_data['name']
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            password_confirm = serializer.validated_data['password_confirm']
            user = User.objects.filter(email=email).first()

            if password != password_confirm:
                return Response({"error": "Введенные пароли не совпадают"}, status=status.HTTP_400_BAD_REQUEST)
            if user is None:
                return Response({"error": "Пользователь не найден"}, status=status.HTTP_404_NOT_FOUND)

            user.set_password(password)
            user.name = name
            user.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                "status": status.HTTP_200_OK,
                "id": user.id,
                "name": name,
                "user": user.email,
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            })

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(request, username=email, password=password)
        if user:  
            if not user.is_verified_email:
                return Response({"error": "Пожалуйста, подтвердите свою почту, введя код подтверждения"}, status=status.HTTP_400_BAD_REQUEST)
            
            user.last_login = now()
            user.save(update_fields=['last_login'])

            refresh = RefreshToken.for_user(user)
            return Response({
                'id': user.id,
                'email': user.email,
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Неверный номер телефона или пароль"}, status=status.HTTP_401_UNAUTHORIZED)
        


class UserProfileView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()

        # Попробуем взять refresh токен (если есть)
        refresh_token = request.data.get("refresh")

        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except TokenError as e:
                return Response({"detail": f"Ошибка с токеном: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)

        # Удаляем пользователя (hard delete)
        user.delete()

        return Response({"detail": "Профиль удалён. Токены отозваны, если были переданы."}, status=status.HTTP_204_NO_CONTENT)
    

class ConfirmNewEmailView(views.APIView):
    serializer_class = VerifyNewEmailSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        code = request.data.get("code")

        if not user.new_email or not user.new_email_verification_code:
            return Response({"detail": "Нет запроса на изменение email."}, status=400)

        if user.new_email_verification_code != code:
            return Response({"detail": "Неверный код подтверждения."}, status=400)

        # Заменить email
        user.email = user.new_email
        user.new_email = None
        user.new_email_verification_code = None
        user.new_email_verification_code_created_at = None
        user.is_verified_email = True
        user.save()

        return Response({"detail": "Email успешно подтверждён и обновлён."}, status=200)
    


class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        user = self.get_object()
        user.set_password(serializer.validated_data['new_password'])
        user.save()

        return Response({"detail": "Пароль успешно изменён"}, status=status.HTTP_200_OK)
    


class LogoutView(views.APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()

            return Response({"detail": "Вы успешно вышли из системы."}, status=status.HTTP_205_RESET_CONTENT)

        except KeyError:
            return Response({"detail": "Refresh токен обязателен."}, status=status.HTTP_400_BAD_REQUEST)

        except TokenError as e:
            return Response({"detail": f"Недопустимый токен: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        


class ForgotPasswordView(views.APIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Код отправлен на вашу почту."}, status=status.HTTP_200_OK)


class PasswordResetConfirmView(views.APIView):
    serializer_class = PasswordResetConfirmSerializer

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"detail": "Пароль успешно изменён."}, status=status.HTTP_200_OK)
    



