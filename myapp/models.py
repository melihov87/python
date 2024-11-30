from django.db import models
from django.db.models import DateTimeField
from django.utils.timezone import now
from datetime import timedelta
import random
import string


# Таблица для хранения данных аутентификации
class PhoneAuth(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    auth_code = models.CharField(max_length=4)
    created_at: DateTimeField = models.DateTimeField(auto_now_add=True)

    # is_code_valid -Проверяет, действителен ли код.
    def is_code_valid(self):
        """Код действует в течение 5 минут"""
        # Если код был создан менее чем 5 минут назад, метод возвращает True, иначе — False.
        return now() <= self.created_at + timedelta(minutes=5)


# Таблица пользователей
class UserProfile(models.Model):
    phone_number = models.CharField(max_length=15, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    invite_code = models.CharField(max_length=6, unique=True, null=True, blank=True)
    activated_invite_code = models.CharField(max_length=6, null=True, blank=True)

    # Обратная связь: пользователи, которые активировали инвайт-код
    invited_users = models.ManyToManyField("self", symmetrical=False,
                                           related_name="invited_by", through="InviteLink", blank=True)

    # Если инвайт-код не был задан, он автоматически генерировался.
    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.invite_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.phone_number


# Таблица отправленных приглашений
class InviteLink(models.Model):
    # Поле для хранения ссылки на пользователя, который отправил приглашение.
    user = models.ForeignKey(UserProfile, related_name='invites', on_delete=models.CASCADE)
    # Поле для хранения ссылки на пользователя, который был приглашен.
    invited_user = models.ForeignKey(UserProfile, related_name='invitations', on_delete=models.CASCADE)
    # Поле для хранения даты и времени, когда приглашение было активировано.
    activated_at = models.DateTimeField(auto_now_add=True)
