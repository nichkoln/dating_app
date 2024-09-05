#import hashlib
#import hmac
import json
#import time
import logging
import asyncio

#from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
#from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
from .bot import send_message
from .forms import CustomUserChangeForm, MessageForm
from .models import CustomUser, Like, Match, Chat, Message #pylint: disable=unused-import


logger = logging.getLogger('telegram_login')

def generate_unique_username(base_username):
    counter = 1
    unique_username = base_username
    while CustomUser.objects.filter(username=unique_username).exists():
        unique_username = f"{base_username}_{counter}"
        counter += 1
    return unique_username

def login_view(request):
    bot_username = 'dtxapp_bot' 
    logger.info("login.html rendered")
    return render(request, 'login.html', {'bot_username': bot_username})


@login_required
def my_profile_view(request):
    user = request.user  # Получаем текущего пользователя

   

    context = {
        'user': user,
    }
    return render(request, 'profiles/my_profile.html', context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        logger.debug(f"POST data: {request.POST}") # pylint: disable=logging-fstring-interpolation
        logger.debug(f"FILES data: {request.FILES}")# pylint: disable=logging-fstring-interpolation
        
        form = CustomUserChangeForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            logger.info("Profile updated successfully.")
            return redirect('my_profile')
        else:
            logger.error(f"Form errors: {form.errors}") # pylint: disable=logging-fstring-interpolation
    else:
        form = CustomUserChangeForm(instance=request.user)
    
    return render(request, 'profile_edit.html', {'form': form})

@login_required
def swipe_profile(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        direction = data.get('direction')
        logger.info(f"Swiping profile {pk} to the {direction}") # pylint: disable=logging-fstring-interpolation

        try:
            profile = CustomUser.objects.get(pk=pk)
            user = request.user

            if direction == 'right':
                if not Like.objects.filter(from_user=user, to_user=profile).exists():
                    Like.objects.create(from_user=user, to_user=profile)
                    asyncio.run(send_message(profile.telegram_id, f"You have a new like from {user.first_name} {user.last_name}!", "https://www.dtxapp.ru"))

                    if Like.objects.filter(from_user=profile, to_user=user).exists():
                        Match.objects.create(user1=user, user2=profile)
                        chat = Chat.objects.create(user1=user, user2=profile) # pylint: disable=no-member
                        asyncio.run(send_message(profile.telegram_id, f"You have a new match with {user.first_name} {user.last_name}!", "https://www.dtxapp.ru"))
                        asyncio.run(send_message(user.telegram_id, f"You have a new match with {profile.first_name} {profile.last_name}!", "https://www.dtxapp.ru"))

            logger.info(f"Profile {profile} swiped {direction}")# pylint: disable=logging-fstring-interpolation
            return JsonResponse({'message': f'Profile {profile.id} swiped {direction} successfully.'})
        except CustomUser.DoesNotExist:  # pylint: disable=no-member
            logger.error(f"Profile {pk} does not exist")# pylint: disable=logging-fstring-interpolation
            return JsonResponse({'error': 'Profile does not exist'}, status=404)
    else:
        logger.error("Invalid request method")
        return JsonResponse({'error': 'Invalid request method'}, status=400)



@login_required
def like_list(request):
    likes_received = Like.objects.filter(to_user=request.user)
    return render(request, 'like_list.html', {'likes_recieved': likes_received})

def auto_login(request):
    logger.info("Auto login started")

    # Получение данных из параметров URL
    telegram_id = request.GET.get('id')
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    username = request.GET.get('username', '')

    if not telegram_id:
        logger.error("No telegram ID provided.")
        return HttpResponse("No telegram ID provided.", status=400)

    logger.debug(f"Telegram ID: {telegram_id}")# pylint: disable=logging-fstring-interpolation
    logger.debug(f"First name: {first_name}")# pylint: disable=logging-fstring-interpolation
    logger.debug(f"Last name: {last_name}")# pylint: disable=logging-fstring-interpolation
    logger.debug(f"Username: {username}")# pylint: disable=logging-fstring-interpolation

    base_username = f"tg_{telegram_id}"
    user, created = CustomUser.objects.get_or_create(
        telegram_id=telegram_id,
        defaults={
            'username': generate_unique_username(base_username),
            'first_name': first_name,
            'last_name': last_name,
        }
    )

    if created:
        user.set_unusable_password()
        user.save()
        logger.info(f"New user created: {user.username}")# pylint: disable=logging-fstring-interpolation

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    logger.info(f"User logged in: {user.username}")# pylint: disable=logging-fstring-interpolation

    return redirect('profile_list')

@login_required
def profile_list(request):
    all_profiles = CustomUser.objects.exclude(id=request.user.id)
    liked_profiles = Like.objects.filter(from_user=request.user).values_list('to_user_id', flat=True)
    profiles_to_show = all_profiles.exclude(id__in=liked_profiles)

    context = {
        'profiles': profiles_to_show,
    }
    return render(request, 'profile_list.html', context)

def profile_detail(request, pk):
    profile = CustomUser.objects.get(pk=pk)
    return render(request, 'profile_detail.html', {'profile': profile})

@login_required
def chat_list(request):
    chats = Chat.objects.filter(user1=request.user) | Chat.objects.filter(user2=request.user) # pylint: disable=no-member
    return render(request, 'chat_list.html', {'chats': chats})

@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user != chat.user1 and request.user != chat.user2:
        return redirect('chat_list')

    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest'

    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat = chat
            message.sender = request.user
            message.save()
            
            other_user = chat.user1 if chat.user2 == request.user else chat.user2
            asyncio.run(send_message(other_user.telegram_id, f"New message from {request.user.first_name} {request.user.last_name}", "https://www.dtxapp.ru"))
            logger.debug(f"Message sent from {request.user} to {other_user}")
            if is_ajax:
                html = render_to_string('chat/messages.html', {'chat': chat, 'request': request})
                return JsonResponse({'html': html})
            return redirect('chat_detail', chat_id=chat.id)
        else:
            logger.debug('Form is not valid')
    else:
        form = MessageForm()
        logger.debug('GET request received for chat: %s', chat_id)

    if is_ajax:
        logger.debug('AJAX GET request received for chat: %s', chat_id)
        html = render_to_string('chat/messages.html', {'chat': chat, 'request': request})
        return JsonResponse({'html': html})
    
    return render(request, 'chat_detail.html', {'chat': chat, 'form': form})