from urllib.parse import parse_qs

import jwt
from django.conf import settings

from .jwt_auth import ServiceHubUser


class JWTAuthMiddleware:
    """ASGI middleware that authenticates a websocket connection from a
    `?token=<access_token>` query param, since browsers can't attach an
    Authorization header to a WebSocket handshake. Attaches the same
    lightweight ServiceHubUser used by the REST views to `scope['user']`."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        query_string = scope.get("query_string", b"").decode()
        token = parse_qs(query_string).get("token", [None])[0]

        scope["user"] = None
        if token:
            try:
                claims = jwt.decode(token, settings.JWT_ACCESS_SECRET, algorithms=["HS256"])
                scope["user"] = ServiceHubUser(claims)
            except jwt.InvalidTokenError:
                scope["user"] = None

        return await self.app(scope, receive, send)
