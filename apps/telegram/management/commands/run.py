from django.core.management.base import BaseCommand
from aiogram import executor
from apps.telegram.management.commands.bot_instance import dp
from apps.telegram.management.commands.business import register_handlers
from apps.telegram.management.commands.cklient import register_handlers_client

class Command(BaseCommand):

    help = 'Starts the Telegram bot'
    def handle(self, *args, **options):
        register_handlers(dp)
        register_handlers_client(dp)
        executor.start_polling(dp, skip_updates=True)