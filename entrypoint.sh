#!/bin/sh

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Применение миграций..."
    python manage.py migrate

    echo "Сбор статических файлов..."
    python manage.py collectstatic --noinput
fi

if [ "$LOAD_FIXTURES" = "true" ]; then
    python manage.py loaddata initial_data.json
fi

exec "$@"
