import random
import time
from django.utils.timezone import now
from .serializers import SendCodeSerializer, VerifyCodeSerializer, UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import PhoneAuth, UserProfile, InviteLink


class SendCodeAPIView(APIView):
    # Метод, который обрабатывает POST-запросы для отправки кода на телефон.
    def post(self, request):
        # Передача данных в сериалазатор
        serializer = SendCodeSerializer(data=request.data)
        # Проверка данных на валидность
        serializer.is_valid(raise_exception=True)

        # Извлечение номера телефона для генерации кода
        phone_number = serializer.validated_data['phone_number']

        # Сгенерировать код
        auth_code = f"{random.randint(1000, 9999)}"

        # Эмулировать задержку
        time.sleep(2)

        # Сохранение или обновление кода в базе данных
        PhoneAuth.objects.update_or_create(
            phone_number=phone_number,
            defaults={'auth_code': auth_code, 'created_at': now()}
        )

        # Логируем отправку в консоль
        print(f"Отправлен код: {auth_code} для номера {phone_number}")

        # Дублируем код для отображения в ответе
        return Response({'message': f"Отправлен код: {auth_code} для номера {phone_number}"}, status=status.HTTP_200_OK)


class VerifyCodeAPIView(APIView):
    def post(self, request):
        # Передача номера телефона и кода в сериализатор
        serializer = VerifyCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phone_number = serializer.validated_data['phone_number']
        auth_code = serializer.validated_data['auth_code']

        # Ищем запись по номеру телефона
        # Если запись не найдена — возвращаем ошибку
        try:
            phone_auth = PhoneAuth.objects.get(phone_number=phone_number)
        except PhoneAuth.DoesNotExist:
            return Response({'error': 'Номер телефона не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Если код устарел (прошло более 5 минут) — возвращаем ошибку
        if not phone_auth.is_code_valid():
            return Response({'error': 'Код истёк'}, status=status.HTTP_400_BAD_REQUEST)

        # Если введенный код не совпадает с сохраненным — возвращаем ошибку
        if phone_auth.auth_code != auth_code:
            return Response({'error': 'Неверный код'}, status=status.HTTP_400_BAD_REQUEST)

        # Создать пользователя, если его нет в базе данных
        user, created = UserProfile.objects.get_or_create(phone_number=phone_number)

        if created:
            # Сохранить объект, чтобы вызвать генерацию инвайт-кода
            user.save()

            # Логирование случайно сгенерированного инвайт-кода
            print(f"Сгенерирован инвайт-код: {user.invite_code} для пользователя {phone_number}")

        # Успешная авторизация
        return Response({
            'message': 'Авторизация успешна',
            'user': UserProfileSerializer(user).data,
            'invite_code': user.invite_code  # Передача инвайт-кода в ответе
        }, status=status.HTTP_200_OK)


class UserProfileAPIView(APIView):
    def get(self, request, phone_number):
        # Поиск пользователя по номеру телефона.
        try:
            user = UserProfile.objects.get(phone_number=phone_number)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Получаем список пользователей, которые использовали инвайт-код текущего пользователя
        invited_users = user.invited_users.all()

        # Создаем список номеров телефонов пользователей, которые использовали инвайт-код
        invited_users_phone_numbers = [invited_user.phone_number for invited_user in invited_users]

        # Возвращаем данные профиля вместе с пользователями, которые использовали инвайт-код
        serializer = UserProfileSerializer(user)
        return Response({
            'profile': serializer.data,
            'invited_users': invited_users_phone_numbers
        }, status=status.HTTP_200_OK)

    def post(self, request, phone_number):
        # Поиск пользователя по номеру телефона.
        try:
            user = UserProfile.objects.get(phone_number=phone_number)
        except UserProfile.DoesNotExist:
            return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)

        # Получение инвайт-кода из данных запроса
        invite_code = request.data.get('invite_code')

        if invite_code:
            try:
                invite_user = UserProfile.objects.get(invite_code=invite_code)

                if user.activated_invite_code:
                    return Response({'message': 'Инвайт-код уже активирован.'}, status=status.HTTP_400_BAD_REQUEST)

                user.activated_invite_code = invite_code
                user.save()

                # Добавляем связь между пользователями
                InviteLink.objects.create(user=invite_user, invited_user=user)

                return Response({'message': 'Инвайт-код активирован успешно.'}, status=status.HTTP_200_OK)

            except UserProfile.DoesNotExist:
                return Response({'error': 'Инвайт-код не существует.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'error': 'Инвайт-код не передан.'}, status=status.HTTP_400_BAD_REQUEST)
