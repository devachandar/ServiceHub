from .models import CustomerProfile, Preference


def handle_user_registered(payload):
    profile, created = CustomerProfile.objects.get_or_create(
        user_id=payload["userId"],
        defaults={"email": payload["email"], "full_name": payload["fullName"]},
    )
    if created:
        Preference.objects.create(profile=profile)


HANDLERS = {
    "UserRegistered": handle_user_registered,
}
