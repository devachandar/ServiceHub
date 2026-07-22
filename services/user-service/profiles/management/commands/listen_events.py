"""
Generic Redis Pub/Sub listener. Each service that subscribes to events
copies this file into <app>/management/commands/listen_events.py and
customizes CHANNELS + the handler dispatch table in `events_handlers.py`
of that same app. Run with:

    python manage.py listen_events

Kept in its own container/process (see docker-compose.yml) so it can
restart independently of the web process.
"""
import json

import redis
from django.conf import settings
from django.core.management.base import BaseCommand

from .. import events_handlers


class Command(BaseCommand):
    help = "Subscribe to domain events on Redis Pub/Sub and dispatch to handlers"

    def handle(self, *args, **options):
        client = redis.Redis.from_url(settings.REDIS_URL)
        pubsub = client.pubsub()
        channels = list(events_handlers.HANDLERS.keys())
        pubsub.subscribe(*channels)
        self.stdout.write(self.style.SUCCESS(f"Subscribed to: {', '.join(channels)}"))

        for message in pubsub.listen():
            if message["type"] != "message":
                continue
            try:
                body = json.loads(message["data"])
                event_name = body["event"]
                payload = body["payload"]
            except (ValueError, KeyError):
                self.stderr.write("Received malformed event, skipping")
                continue

            handler = events_handlers.HANDLERS.get(event_name)
            if not handler:
                continue
            try:
                handler(payload)
                self.stdout.write(f"Handled {event_name}")
            except Exception as exc:  # noqa: BLE001
                self.stderr.write(f"Error handling {event_name}: {exc}")
