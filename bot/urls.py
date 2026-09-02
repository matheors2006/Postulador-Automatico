from django.urls import path

from bot.api.webhooks import whatsapp_webhook

app_name = 'bot'

urlpatterns = [
    path('webhook/', whatsapp_webhook, name='whatsapp_webhook'),
]
