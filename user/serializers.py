from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import random
from .tasks import send_verificaation_code, send_password_reset_code, send_verificaation_code_to_new_email
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('email',)

class VerifyEmailSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    verification_code = serializers.CharField(required=True, style={'input_type': 'verification_code'})


class VerifyNewEmailSerializer(serializers.Serializer):
    code = serializers.CharField(required=True, style={'input_type': 'verification_code'})


class SetPasswordSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})
    password_confirm = serializers.CharField(required=True, style={'input_type': 'password'})
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'password', 'role',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', 'Пользователь')
            )
        return user
    

class UserLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True, allow_blank=False, allow_null=False)
    password = serializers.CharField(required=True, allow_blank=False, allow_null=False)


class UserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'avatar', 
            'registered_at', 'updated_at'
        ]

    def update(self, instance, validated_data):
        request = self.context.get('request')
        new_email = validated_data.get('email')
        old_email = instance.email

        if new_email and new_email != old_email:
            # Генерация 4-значного кода
            code = str(random.randint(1000, 9999))
            instance.new_email = new_email
            instance.new_email_verification_code = code
            instance.new_email_verification_code_created_at = timezone.now()

            try:
                # Отправка кода подтверждения на новую почту
                send_verificaation_code_to_new_email.delay(instance.id)  # укажи нужную задачу
                request._email_changed = True
                instance.save()
            except Exception as e:
                raise ValidationError({"email": "Ошибка при отправке письма. Email не изменён."})

        validated_data.pop('email', None)
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        data = super().to_representation(instance)
        request = self.context.get('request')
        if hasattr(request, '_email_changed') and request._email_changed:
            data['message'] = 'На ваш новый email отправлено письмо с кодом подтверждения. Пожалуйста, подтвердите адрес.'
        return data
   
    


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Старый пароль указан неверно")
        return value



class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if not User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return value

    def save(self):
        user = User.objects.get(email=self.validated_data['email'])
        code = str(random.randint(1000, 9999))
        user.password_reset_code = code
        user.password_reset_code_created_at = timezone.now()
        user.save()
        send_password_reset_code.delay(user.id)


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(write_only=True)

    def validate(self, data):
        try:
            user = User.objects.get(email=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверный email или код.")

        # Проверка срока действия кода (например, 10 минут)
        if user.password_reset_code != data['code']:
            raise serializers.ValidationError("Неверный код подтверждения.")
        if timezone.now() - user.password_reset_code_created_at > timedelta(minutes=10):
            raise serializers.ValidationError("Код устарел. Запросите новый.")

        self.user = user
        return data

    def save(self):
        self.user.set_password(self.validated_data['new_password'])
        self.user.password_reset_code = None
        self.user.password_reset_code_created_at = None
        self.user.save()