from django import template

register = template.Library()

@register.filter
def chat_partner(chat, user):
    return chat.user1 if chat.user2 == user else chat.user2

@register.filter
def chat_partner_name(chat, user):
    partner = chat.user1 if chat.user2 == user else chat.user2
    return f"{partner.first_name} {partner.last_name}"
