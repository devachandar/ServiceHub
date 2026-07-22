from django.utils import timezone as djtz
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .events import publish_event
from .models import AuditLog, RefreshToken, User
from .permissions import IsAuthenticatedStateless, IsRole
from .serializers import LoginSerializer, RegisterSerializer, UserPublicSerializer
from .tokens import generate_refresh_token, hash_token, issue_access_token


class RegisterView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        user = User(email=data["email"], full_name=data["full_name"], role=data["role"])
        user.set_password(serializer.initial_data["password"])
        user.save()

        AuditLog.objects.create(user=user, action="USER_REGISTERED", metadata={"role": user.role})

        publish_event(
            "UserRegistered",
            {
                "userId": str(user.id),
                "email": user.email,
                "fullName": user.full_name,
                "role": user.role,
            },
        )

        access_token = issue_access_token(user)
        raw_refresh, hashed, expires_at = generate_refresh_token()
        RefreshToken.objects.create(user=user, token_hash=hashed, expires_at=expires_at)

        return Response(
            {
                "user": UserPublicSerializer(user).data,
                "accessToken": access_token,
                "refreshToken": raw_refresh,
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response({"error": "Invalid email or password"}, status=401)

        if user.status == "suspended":
            return Response({"error": "This account has been suspended"}, status=403)
        if not user.check_password(password):
            return Response({"error": "Invalid email or password"}, status=401)

        access_token = issue_access_token(user)
        raw_refresh, hashed, expires_at = generate_refresh_token()
        RefreshToken.objects.create(user=user, token_hash=hashed, expires_at=expires_at)
        AuditLog.objects.create(user=user, action="USER_LOGIN")

        return Response(
            {
                "user": UserPublicSerializer(user).data,
                "accessToken": access_token,
                "refreshToken": raw_refresh,
            }
        )


class RefreshView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        raw_refresh = request.data.get("refreshToken")
        if not raw_refresh:
            return Response({"error": "refreshToken is required"}, status=400)

        record = (
            RefreshToken.objects.select_related("user")
            .filter(token_hash=hash_token(raw_refresh), revoked=False, expires_at__gt=djtz.now())
            .first()
        )
        if not record:
            return Response({"error": "Refresh token is invalid or expired"}, status=401)

        return Response({"accessToken": issue_access_token(record.user)})


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        raw_refresh = request.data.get("refreshToken")
        if raw_refresh:
            RefreshToken.objects.filter(token_hash=hash_token(raw_refresh)).update(revoked=True)
        return Response(status=204)


class MeView(APIView):
    permission_classes = [IsAuthenticatedStateless]

    def get(self, request):
        try:
            user = User.objects.get(id=request.user.id)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)
        return Response(UserPublicSerializer(user).data)


class InternalUserDetailView(APIView):
    """Service-to-service lookup so other services can resolve an email or
    display name from a user_id without duplicating the users table."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            return Response({"error": "User not found"}, status=404)
        return Response(UserPublicSerializer(user).data)


class AdminUserListView(APIView):
    permission_classes = [IsRole("admin")]

    def get(self, request):
        users = User.objects.order_by("-created_at")[:200]
        return Response(UserPublicSerializer(users, many=True).data)


class AdminUserStatusView(APIView):
    permission_classes = [IsRole("admin")]

    def patch(self, request, user_id):
        new_status = request.data.get("status")
        if new_status not in ("active", "suspended"):
            return Response({"error": "status must be 'active' or 'suspended'"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except (User.DoesNotExist, ValueError):
            return Response({"error": "User not found"}, status=404)

        user.status = new_status
        user.save(update_fields=["status", "updated_at"])
        AuditLog.objects.create(
            user_id=request.user.id, action="USER_STATUS_CHANGED", metadata={"target": str(user_id), "status": new_status}
        )
        return Response(UserPublicSerializer(user).data)
