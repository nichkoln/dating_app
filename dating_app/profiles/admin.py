from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Like, Match, Chat, Message

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['username', 'email', 'bio', 'location', 'birth_date', 'is_staff', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('bio', 'location', 'birth_date')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('bio', 'location', 'birth_date')}),
    )
class LikeAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'timestamp')
    search_fields = ('from_user__username', 'to_user__username')

class MatchAdmin(admin.ModelAdmin):
    list_display = ('user1', 'user2', 'timestamp')
    search_fields = ('user1__username', 'user2__username')
    
class MessageInline(admin.TabularInline):
    model = Message
    extra = 1

@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    list_display = ('id', 'user1', 'user2', 'created_at')
    search_fields = ('user1__username', 'user2__username')
    inlines = [MessageInline]

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'chat', 'sender', 'created_at')
    search_fields = ('chat__user1__username', 'chat__user2__username', 'sender__username')
    list_filter = ('created_at',)

admin.site.register(Like, LikeAdmin)
admin.site.register(Match, MatchAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
