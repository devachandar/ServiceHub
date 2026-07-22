import hashlib
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from django.conf import settings


def issue_access_token(user):
    now = datetime.now(timezone.utc)
    claims = {
        "user_id": str(user.id),
        "email": user.email,
        "role": user.role,
        "full_name": user.full_name,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_ACCESS_TTL_MINUTES),
    }
    return jwt.encode(claims, settings.JWT_ACCESS_SECRET, algorithm="HS256")


def hash_token(raw_token: str) -> str:
    return hashlib.sha256(raw_token.encode()).hexdigest()


def generate_refresh_token():
    raw = secrets.token_hex(48)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TTL_DAYS)
    return raw, hash_token(raw), expires_at
