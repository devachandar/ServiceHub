#!/bin/sh
set -e

python - <<'PYEOF'
import os, socket, time, urllib.parse as up
url = os.environ.get("DATABASE_URL", "")
if url:
    parsed = up.urlparse(url)
    host, port = parsed.hostname, parsed.port or 5432
    for _ in range(60):
        try:
            socket.create_connection((host, port), timeout=2).close()
            break
        except OSError:
            print("waiting for postgres...")
            time.sleep(2)
PYEOF

python manage.py migrate --noinput

case "$1" in
  web)
    exec gunicorn config.wsgi:application --bind 0.0.0.0:8009 --workers 3
    ;;
  asgi)
    exec daphne -b 0.0.0.0 -p 8009 config.asgi:application
    ;;
  worker)
    exec celery -A config worker -l info -Q media_events --concurrency=2
    ;;
  listener)
    exec python manage.py listen_events
    ;;
  *)
    exec "$@"
    ;;
esac
