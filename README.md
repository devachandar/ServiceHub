# ServiceHub

A microservices marketplace for booking verified service providers -
think Thumbtack/Urban Company: customers search pros, book a time slot,
pay, message the provider, and leave a review; providers manage a business
profile, services, schedule, and earnings; admins verify providers and
watch platform KPIs.

Built as a system-design portfolio project on the exact stack from the
design doc: **Django REST Framework, PostgreSQL, Redis, Celery, RabbitMQ,
Elasticsearch, React + TypeScript + Redux Toolkit + React Query + MUI.**

## Architecture

```
React (TS, Redux Toolkit, React Query, MUI)
            │
            ▼
   Nginx API Gateway  ──/api/auth────────► Auth Service ─────────► Postgres (auth_db)
            │           ──/api/users───────► User Service ──────────► Postgres (user_db)
            │           ──/api/providers──► Provider Service ──────► Postgres (provider_db)
            │           ──/api/bookings───► Booking Service ───────► Postgres (booking_db)
            │           ──/api/reviews────► Review Service ────────► Postgres (review_db)
            │           ──/api/payments───► Payment Service ───────► Postgres (payment_db)
            │           ──/api/search─────► Search Service ────────► Elasticsearch
            │           ──/api/media──────► Media Service ─────────► local disk / S3
            │           ──/api/analytics──► Analytics Service ─────► Postgres (analytics_db)
            │           ──/api/chat & /ws/chat──► Chat Service (Django Channels) ─► Postgres (chat_db)
            │
            └── (async) Notification Service ─► email (SMTP or console)

Events (Redis Pub/Sub): UserRegistered · ProviderCreated/Updated/Verified ·
BookingCreated/Cancelled/Completed/Rescheduled · PaymentCaptured ·
ReviewCreated
```

### The two-layer async design

This is the one architectural decision worth understanding before reading
the code: **Redis Pub/Sub is the cross-service event bus, Celery + RabbitMQ
is the durable task queue *inside* a service.** They solve different
problems and the doc's tech list calls for both, so both are used for what
they're actually good at:

- **Redis Pub/Sub** gives true fan-out - when Booking Service publishes
  `BookingCreated`, Payment Service, Notification Service, and Analytics
  Service each get their own copy and react independently, with no
  knowledge of each other. Every subscribing service runs a
  `listen_events` management command (its own container/process) that
  subscribes to the channels it cares about.
- **Celery + RabbitMQ** picks up from there for anything that needs
  retries/backoff if it fails - capturing a payment, sending an email.
  Those listeners don't do the risky work inline; they call `.delay()` on
  a Celery task, which is what actually hits the (simulated) payment
  gateway or SMTP server, with Celery's retry semantics protecting it.

A single message queue can't natively broadcast one message to multiple
independent consumers (a queued task goes to whichever worker picks it up
first) - that's exactly the gap Redis Pub/Sub fills here, while Celery
still does the job it's built for.

### Stateless JWT auth

Only **Auth Service** has a real `User` table. Every other service
verifies the same HS256-signed access token locally (`jwt_auth.py`,
copied into each service like the event-bus helper) and builds a
lightweight, non-persisted user object from the claims - no per-request
call back to Auth Service, no shared session store. This is also why Auth
and User are separate services in the design: Auth owns *who you are*,
User owns *your profile*.

### Service boundaries

| Service | Owns | Port |
|---|---|---|
| `auth-service` | credentials, JWT, refresh tokens, audit log | 8001 |
| `user-service` | customer profile, addresses, saved providers, preferences | 8002 |
| `provider-service` | business profile, verification, services, pricing, working hours | 8003 |
| `booking-service` | appointments, availability, cancellation/reschedule | 8004 |
| `review-service` | ratings, comments, moderation | 8005 |
| `payment-service` | invoices, transactions, refunds, payouts | 8006 |
| `search-service` | Elasticsearch index, full-text/geo search, autocomplete | 8007 |
| `chat-service` | messages, read status (Django Channels + WebSocket) | 8008 |
| `media-service` | file uploads (local disk by default, S3 when configured) | 8009 |
| `analytics-service` | KPIs, revenue, growth | 8010 |
| `notification-service` | email (booking confirmations, receipts, review alerts) | 8011 |
| `gateway` (Nginx) | routing, rate limiting, CORS, WebSocket upgrade | 8080 |

Booking availability is a good example of the ownership split in
practice: **Provider Service owns the *rules*** (weekly working hours,
time off, service duration) while **Booking Service owns the
*calendar*** (which slots are actually taken). Booking Service fetches
the rules over HTTP and cross-references them against its own rows -
Provider Service never needs to know a single thing about appointments.

## Running it locally

Requirements: Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up --build
```

First boot takes a minute or two (Postgres creating 11 databases,
Elasticsearch initializing, ~20 containers total). Then open:

- **App:** http://localhost:3000
- **API gateway:** http://localhost:8080/api
- **RabbitMQ management UI:** http://localhost:15672 (servicehub / servicehub)
- **Elasticsearch:** http://localhost:9200

### Try the flow end to end

1. **Register as a provider** at `/register`, then go to the dashboard and
   fill out the **Profile** tab, add a **Service**, and set your **Hours**.
   - As an admin (see below), verify the provider so it's bookable and
     searchable.
2. **Register as a customer** in a second browser/incognito window, search
   for the provider, pick a service, choose an open time slot, and book it.
   - `BookingCreated` fires → Payment Service creates a pending invoice,
     Notification Service emails both sides (or logs to console), Analytics
     Service counts it.
3. Pay the invoice from **My bookings** - this queues a Celery task that
   "captures" the payment (simulated gateway, ~5% chance of a retried
   timeout so the retry path is real) and confirms the booking.
4. **Message the provider** from their profile page - this opens a
   WebSocket-backed chat thread.
5. As the provider, mark the booking **completed**; as the customer, leave
   a **review** - this updates the provider's average rating via Review →
   Provider Service, and re-indexes it in Elasticsearch via the event bus.

### Creating an admin user

There's no public admin signup (by design). Register normally, then flip
the role directly in Postgres:

```bash
docker compose exec postgres psql -U servicehub -d auth_db \
  -c "UPDATE accounts_user SET role = 'admin' WHERE email = 'you@example.com';"
```

## Running a single service without Docker

```bash
cd services/auth-service
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgres://servicehub:servicehub@localhost:5432/auth_db
export JWT_ACCESS_SECRET=dev-only-jwt-secret-change-me
export REDIS_URL=redis://localhost:6379/0
python manage.py migrate
python manage.py runserver 0.0.0.0:8001
```

Services that consume events also need the listener running:
`python manage.py listen_events`. Services with a Celery worker
(`payment-service`, `notification-service`) additionally need:
`celery -A config worker -l info -Q <queue_name>` with RabbitMQ reachable.

## What's simplified vs. the original design

Sized for a portfolio, not 10M customers - a few deliberate cuts, so
they're easy to extend rather than surprises:

- **Analytics** aggregates daily counters in Postgres via the event
  listener, not a real OLAP/warehouse pipeline.
- **Payment capture** simulates a gateway (with a small chance of a
  retried "timeout" to exercise Celery's retry path) rather than calling
  Stripe/Braintree - swap `capture_payment_task` for a real SDK call and
  the rest of the flow (invoice → Celery → `PaymentCaptured` event →
  booking confirmation) doesn't change.
- **Media Service** defaults to local disk (`STORAGE_DRIVER=local`) so
  the project runs without an AWS account; set `STORAGE_DRIVER=s3` plus
  the AWS env vars in `.env` to use real S3.
- **Chat** attachments accept a URL (upload to Media Service first, then
  pass the URL) rather than direct binary upload over the socket.
- **Infra** (CloudFront, ALB, ECS, GitHub Actions) is out of scope for
  local dev - the Dockerfiles are meant to make wiring up the real AWS
  deployment a config change, not a rewrite.

## Repo layout

```
servicehub/
├── docker-compose.yml
├── .env.example
├── infra/
│   ├── nginx/                  # API Gateway config
│   └── postgres-init/          # creates one DB per service on first boot
├── services/
│   ├── auth-service/
│   ├── user-service/
│   ├── provider-service/
│   ├── booking-service/
│   ├── review-service/
│   ├── payment-service/
│   ├── search-service/
│   ├── chat-service/
│   ├── media-service/
│   ├── analytics-service/
│   └── notification-service/
└── frontend/
```

Each service follows the same internal shape: `config/` (Django settings,
Celery app, ASGI/WSGI entrypoints) and one domain app (e.g. `bookings/`)
with `models.py`, `serializers.py`, `views.py`, `urls.py`, and - where
relevant - `events.py` (publish), `events_handlers.py` +
`management/commands/listen_events.py` (subscribe), and `tasks.py`
(Celery).
