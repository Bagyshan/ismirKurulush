from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils.translation import gettext_lazy as _
from .managers import UserManager
from django.core.exceptions import ValidationError

def validate_kg_phone(value):
    if value.startswith("996") and len(value) == 12 and value[3:].isdigit():
        return
    raise ValidationError(_('Номер телефона должен начинаться с 996 и содержать ровно 9 цифр.'))


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(_('Имя'), max_length=150, blank=True)
    INN = models.PositiveBigIntegerField(_('ИНН'), blank=True, null=True)
    email = models.EmailField(
        _('Email'),
        unique=True,
        db_index=True)
        # validators=[validate_kg_phone]
    # )
    avatar = models.ImageField(_("Аватарка"), upload_to="avatar/", default=None, null=True, blank=True)
    is_superuser = models.BooleanField(_('Суперпользователь'), default=False)
    is_delete = models.BooleanField(_('Удален'), default=False)
    is_active = models.BooleanField(_('Активен'), default=True)
    is_staff = models.BooleanField(_('Сотрудник'), default=False)
    is_verified_email = models.BooleanField(_('Email подтвержден'), default=False)
    verification_code = models.CharField(_('Код подтверждения'), max_length=6, blank=True, null=True)
    verification_code_created_at = models.DateTimeField(_('Дата создания кода подтверждения'), blank=True, null=True)
    password_reset_code = models.CharField(_("Код сброса пароля"), max_length=6, null=True, blank=True)
    password_reset_code_created_at = models.DateTimeField(_("Дата создания кода сброса пароля"), null=True, blank=True)
    new_email = models.EmailField(_('Новый email'), null=True, blank=True)
    new_email_verification_code = models.CharField(_('Код подтверждения нового email'), max_length=6, null=True, blank=True)
    new_email_verification_code_created_at = models.DateTimeField(_('Дата создания кода подтверждения нового email'), null=True, blank=True)
    registered_at = models.DateTimeField(_('Дата регистрации'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Дата обновления'), auto_now=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.email:
            raise ValueError('User must have an email')
        super(User, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if not self.is_superuser:
            self.is_delete = True
            self.save()
        else:
            self.delete()
            
    class Meta:
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')