from .es import index_provider, remove_provider


def handle_provider_created(payload):
    index_provider(payload)


def handle_provider_updated(payload):
    index_provider(payload)


def handle_provider_verified(payload):
    index_provider(payload)


def handle_provider_deleted(payload):
    remove_provider(payload["provider_id"])


HANDLERS = {
    "ProviderCreated": handle_provider_created,
    "ProviderUpdated": handle_provider_updated,
    "ProviderVerified": handle_provider_verified,
    "ProviderDeleted": handle_provider_deleted,
}
