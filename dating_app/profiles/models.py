# models.py
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class CustomUser(AbstractUser):
    bio = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    birth_date = models.DateField(null=True, blank=True)
    telegram_id = models.CharField(max_length=32, unique=True, blank=True, null=True)
    photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    liked_users = models.ManyToManyField('self', through='Like', symmetrical=False, related_name='liked_by')

    def __str__(self):
        return str(self.username)

    objects = CustomUserManager()

class Like(models.Model):
    from_user = models.ForeignKey(CustomUser, related_name='likes_given', on_delete=models.CASCADE)
    to_user = models.ForeignKey(CustomUser, related_name='likes_received', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()  # pylint: disable=no-member

class Match(models.Model):
    user1 = models.ForeignKey(CustomUser, related_name='matches1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(CustomUser, related_name='matches2', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = models.Manager()  # pylint: disable=no-member

    class Meta:
        unique_together = ('user1', 'user2')
        
class Chat(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user1', on_delete=models.CASCADE)
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='chats_as_user2', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between {self.user1} and {self.user2}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='messages_sent', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='messages/images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender} in chat {self.chat.id}" # pylint: disable=no-member
