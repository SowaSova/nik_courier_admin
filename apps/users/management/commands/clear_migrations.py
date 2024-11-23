import os
import sys

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Удаляет все файлы миграций во всех приложениях проекта, кроме __init__.py"

    def handle(self, *args, **options):
        # Получаем список всех установленных приложений
        installed_apps = apps.get_app_configs()

        # Список для хранения путей удалённых файлов
        deleted_files = []

        for app in installed_apps:
            migrations_dir = os.path.join(app.path, "migrations")
            if os.path.isdir(migrations_dir):
                for filename in os.listdir(migrations_dir):
                    file_path = os.path.join(migrations_dir, filename)
                    if filename != "__init__.py" and filename.endswith(".py"):
                        try:
                            os.remove(file_path)
                            deleted_files.append(file_path)
                            self.stdout.write(
                                self.style.SUCCESS(f"Удалён: {file_path}")
                            )
                        except Exception as e:
                            self.stderr.write(
                                self.style.ERROR(
                                    f"Не удалось удалить {file_path}: {e}"
                                )
                            )

        if not deleted_files:
            self.stdout.write(
                self.style.WARNING("Нет файлов миграций для удаления.")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS("Все файлы миграций успешно удалены.")
            )
