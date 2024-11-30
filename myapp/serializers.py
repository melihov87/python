from rest_framework import serializers
from .models import UserProfile


# Отправка кода на номер телефона пользователя.
class SendCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)


# Проверка кода, введенного пользователем.
class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    auth_code = serializers.CharField(max_length=4)


# Автоматическое создание полей, соответствующих модели UserProfile.
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'created_at', 'invite_code', 'activated_invite_code']
