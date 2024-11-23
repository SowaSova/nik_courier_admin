from django.core.management.base import BaseCommand

from tg_bot.main import main


class Command(BaseCommand):
    help = "Запуск Telegram-бота"

    def handle(self, *args, **options):
        import asyncio

        try:
            print("Запуск бота")
            asyncio.run(main())
        except (KeyboardInterrupt, SystemExit):
            print("Бот остановлен")
            # logging.info("Бот остановлен")
