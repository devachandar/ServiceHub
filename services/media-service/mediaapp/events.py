"""
Cross-service event bus (Redis Pub/Sub).

Every service that changes something another service cares about publishes
a small JSON event here instead of calling the other service's API
directly. Interested services run a `listen_events` management command
(see events_listener.py) that subscribes to the channels it cares about and
reacts independently - this is the "Event Bus" from the design doc's
Step 9, kept intentionally simple (Redis pub/sub) rather than Kafka.

Reliability-sensitive work triggered by an event (sending an email,
capturing a payment) is hop over to a Celery task via RabbitMQ from inside
the listener, so it gets retries/backoff for free - see README for the
two-layer rationale (Redis for fan-out, Celery/RabbitMQ for durable work).
"""
import json
from datetime import datetime, timezone

import redis
from django.conf import settings

_client = None


def _get_client():
    global _client
    if _client is None:
        _client = redis.Redis.from_url(settings.REDIS_URL)
    return _client


def publish_event(event_name: str, payload: dict):
    message = json.dumps(
        {
            "event": event_name,
            "payload": payload,
            "emitted_at": datetime.now(timezone.utc).isoformat(),
        },
        default=str,
    )
    _get_client().publish(event_name, message)
