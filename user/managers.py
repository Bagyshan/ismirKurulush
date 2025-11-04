from django.contrib.auth.base_user import BaseUserManager
from django.core.exceptions import ObjectDoesNotExist


class UserManager(BaseUserManager):
    def create_user(self, email=None, password=None, is_staff=False, is_superuser=False, **extra_fields):
        if not password:
            raise ValueError('User must have a password.')

        if not email:
            raise ValueError('User must have an email.')

        model_data = {'is_staff': is_staff, 'is_superuser': is_superuser}

        if email:
            model_data['email'] = email


        user = self.create(**model_data, **extra_fields)
        user.set_password(password)  # Здесь пароль захеширован
        user.save(using=self._db)
        return user

    
    def create_superuser(self, email=None,  password=None, **extra_fields):

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True')

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True')

        user = self.create_user(email, password, **extra_fields)

        return user
    
    def get_user_by_token(self, token):
        try:
            user = self.get(token=token)
            return user
        except ObjectDoesNotExist:
            return None
        