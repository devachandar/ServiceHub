from django.conf import settings
from elasticsearch import Elasticsearch

INDEX = "providers"

_client = None


def get_client():
    global _client
    if _client is None:
        _client = Elasticsearch(settings.ELASTICSEARCH_URL)
    return _client


def ensure_index():
    client = get_client()
    if client.indices.exists(index=INDEX):
        return
    client.indices.create(
        index=INDEX,
        mappings={
            "properties": {
                "business_name": {"type": "text", "fields": {"autocomplete": {"type": "search_as_you_type"}}},
                "bio": {"type": "text"},
                "category": {"type": "keyword"},
                "city": {"type": "keyword"},
                "state": {"type": "keyword"},
                "status": {"type": "keyword"},
                "verification_status": {"type": "keyword"},
                "average_rating": {"type": "float"},
                "review_count": {"type": "integer"},
                "location": {"type": "geo_point"},
                "services": {
                    "type": "nested",
                    "properties": {
                        "name": {"type": "text"},
                        "price": {"type": "float"},
                        "duration_minutes": {"type": "integer"},
                    },
                },
                "created_at": {"type": "date"},
            }
        },
    )


def to_doc(provider):
    doc = {
        "business_name": provider["business_name"],
        "bio": provider.get("bio", ""),
        "category": provider["category"],
        "city": provider["city"],
        "state": provider["state"],
        "status": provider["status"],
        "verification_status": provider["verification_status"],
        "average_rating": provider.get("average_rating", 0),
        "review_count": provider.get("review_count", 0),
        "services": [
            {"name": s["name"], "price": float(s["price"]), "duration_minutes": s["duration_minutes"]}
            for s in provider.get("services", [])
        ],
        "created_at": provider.get("created_at"),
    }
    if provider.get("latitude") is not None and provider.get("longitude") is not None:
        doc["location"] = {"lat": provider["latitude"], "lon": provider["longitude"]}
    return doc


def index_provider(provider):
    ensure_index()
    if provider.get("status") != "active" or provider.get("verification_status") != "verified":
        remove_provider(provider["user_id"])
        return
    get_client().index(index=INDEX, id=provider["user_id"], document=to_doc(provider), refresh=True)


def remove_provider(provider_id):
    try:
        get_client().delete(index=INDEX, id=provider_id, refresh=True)
    except Exception:
        pass
