from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import (auto_login, like_list, my_profile_view, profile_detail,
                    profile_edit, profile_list, swipe_profile, chat_list, chat_detail)

urlpatterns = [
    path('', profile_list, name='profile_list'),
    path('profiles/<int:pk>/', profile_detail, name='profile_detail'),
    path('profile/edit/', profile_edit, name='profile_edit'),
    path('profile/', my_profile_view, name='my_profile'),
    path('login/', auto_login, name='login'),
    path('profiles/<int:pk>/swipe/', swipe_profile, name='swipe_profile'),
     path('likes/', like_list, name='like_list'),
     path('chats/', chat_list, name='chat_list'),
    path('chats/<int:chat_id>/', chat_detail, name='chat_detail')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)