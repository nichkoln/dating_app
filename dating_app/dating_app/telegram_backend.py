from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend
from profiles.models import CustomUser  # Импортируйте вашу модель пользователя
import hmac
import hashlib
import time

class TelegramBackend(BaseBackend):
    def authenticate(self, request, **kwargs):
        # Функция аутентификации через Telegram
        data = kwargs

        # Проверка данных от Telegram
        if not self._validate_telegram_data(data):
            return None

        # Создание или получение пользователя
        user, created = CustomUser.objects.get_or_create(
            telegram_id=data['id'],
            defaults={
                'username': data['id'],
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
            }
        )

        if created:
            user.set_unusable_password()
            user.save()

        return user

    def _validate_telegram_data(self, data):
        auth_date = int(data.get('auth_date', 0))

        # Проверяем, что запрос пришел недавно
        if time.time() - auth_date > 86400:
            return False

        # Проверяем хэш
        check_hash = data.pop('hash')
        token = settings.BOT_TOKEN.encode('utf-8')
        data_check_string = '\n'.join(f"{k}={v}" for k, v in sorted(data.items()))
        secret_key = hmac.new(token, digestmod=hashlib.sha256).digest()
        calculated_hash = hmac.new(secret_key, data_check_string.encode('utf-8'), hashlib.sha256).hexdigest()

        return calculated_hash == check_hash

    def get_user(self, user_id):
        # Получение пользователя по его ID
        try:
            return CustomUser.objects.get(pk=user_id)
        except:
            return None
