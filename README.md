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

```mermaid
flowchart TB
    Client["React · TypeScript<br/>Redux Toolkit · React Query · MUI"]

    Client --> Gateway["Nginx API Gateway<br/><sub>routing · rate limiting · CORS · WS upgrade</sub>"]

    subgraph Core["Core marketplace services"]
        direction LR
        Auth["Auth Service<br/><sub>:8001</sub>"]
        User["User Service<br/><sub>:8002</sub>"]
        Provider["Provider Service<br/><sub>:8003</sub>"]
        Booking["Booking Service<br/><sub>:8004</sub>"]
        Review["Review Service<br/><sub>:8005</sub>"]
        Payment["Payment Service<br/><sub>:8006</sub>"]
    end

    subgraph Support["Search, realtime & support services"]
        direction LR
        Search["Search Service<br/><sub>:8007</sub>"]
        Chat["Chat Service<br/><sub>:8008 · WebSocket</sub>"]
        Media["Media Service<br/><sub>:8009</sub>"]
        Analytics["Analytics Service<br/><sub>:8010</sub>"]
        Notify["Notification Service<br/><sub>:8011</sub>"]
    end

    Gateway -->|/api/auth| Auth
    Gateway -->|/api/users| User
    Gateway -->|/api/providers| Provider
    Gateway -->|/api/bookings| Booking
    Gateway -->|/api/reviews| Review
    Gateway -->|/api/payments| Payment
    Gateway -->|/api/search| Search
    Gateway -->|/ws/chat, /api/chat| Chat
    Gateway -->|/api/media| Media
    Gateway -->|/api/analytics| Analytics

    Auth -.->|"verifies provider"| Provider
    Booking -.->|"reads working hours"| Provider
    Review -.->|"validates booking, updates rating"| Booking
    Review -.->|"updates rating"| Provider

    Auth --> AuthDB[("auth_db")]
    User --> UserDB[("user_db")]
    Provider --> ProviderDB[("provider_db")]
    Booking --> BookingDB[("booking_db")]
    Review --> ReviewDB[("review_db")]
    Payment --> PaymentDB[("payment_db")]
    Analytics --> AnalyticsDB[("analytics_db")]
    Chat --> ChatDB[("chat_db")]
    Search --> ES[("Elasticsearch")]
    Media --> Store[("local disk / S3")]
    Notify --> Mail[["SMTP or console"]]

    classDef svc fill:#0F5E56,stroke:#0A423C,color:#fff
    classDef store fill:#F7F8F7,stroke:#5B655F,color:#1B1F1E
    class Auth,User,Provider,Booking,Review,Payment,Search,Chat,Media,Analytics,Notify svc
    class AuthDB,UserDB,ProviderDB,BookingDB,ReviewDB,PaymentDB,AnalyticsDB,ChatDB,ES,Store,Mail store
```

Dotted arrows above are the only direct service-to-service HTTP calls in the
system (e.g. Booking Service reading a provider's schedule). Everything
else - the stuff that looks like it should be a direct call, like "email
the customer when payment succeeds" - goes through the event bus instead,
so no service ever needs to know who's listening:

```mermaid
sequenceDiagram
    participant B as Booking Service
    participant R as Redis Pub/Sub
    participant P as Payment Service
    participant N as Notification Service
    participant An as Analytics Service

    B->>R: publish BookingCreated
    par fan-out, each subscriber independent
        R-->>P: BookingCreated
        R-->>N: BookingCreated
        R-->>An: BookingCreated
    end
    P->>P: listen_events → create_invoice_task.delay() (Celery/RabbitMQ, retries)
    N->>N: listen_events → send_email_task.delay() (Celery/RabbitMQ, retries)
    An->>An: listen_events → increment today's counters (no Celery needed)
```

Full event catalog: `UserRegistered` · `ProviderCreated/Updated/Verified` ·
`BookingCreated/Cancelled/Completed/Rescheduled` · `PaymentCaptured` ·
`ReviewCreated`.

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
