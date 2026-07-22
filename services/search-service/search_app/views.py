from rest_framework.response import Response
from rest_framework.views import APIView

from .es import INDEX, ensure_index, get_client


class SearchView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_index()
        params = request.query_params
        q = params.get("q")
        category = params.get("category")
        city = params.get("city")
        min_rating = params.get("minRating")
        lat, lon, radius_km = params.get("lat"), params.get("lon"), params.get("radiusKm")
        sort = params.get("sort", "relevance")
        page = int(params.get("page", 1))
        limit = min(int(params.get("limit", 20)), 100)

        must = [{"term": {"status": "active"}}, {"term": {"verification_status": "verified"}}]
        filter_clauses = []

        if q:
            must.append(
                {
                    "multi_match": {
                        "query": q,
                        "fields": ["business_name^3", "bio", "category^2", "city"],
                        "fuzziness": "AUTO",
                    }
                }
            )
        if category:
            filter_clauses.append({"term": {"category": category}})
        if city:
            filter_clauses.append({"term": {"city": city.lower()}})
        if min_rating:
            filter_clauses.append({"range": {"average_rating": {"gte": float(min_rating)}}})
        if lat and lon and radius_km:
            filter_clauses.append(
                {"geo_distance": {"distance": f"{radius_km}km", "location": {"lat": float(lat), "lon": float(lon)}}}
            )

        sort_clause = (
            [{"average_rating": "desc"}]
            if sort == "rating"
            else [{"created_at": "desc"}]
            if sort == "newest"
            else ["_score"]
        )

        result = get_client().search(
            index=INDEX,
            from_=(page - 1) * limit,
            size=limit,
            query={"bool": {"must": must, "filter": filter_clauses}},
            sort=sort_clause,
        )

        return Response(
            {
                "total": result["hits"]["total"]["value"],
                "page": page,
                "limit": limit,
                "results": [{"id": hit["_id"], "score": hit["_score"], **hit["_source"]} for hit in result["hits"]["hits"]],
            }
        )


class AutocompleteView(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        ensure_index()
        q = request.query_params.get("q")
        if not q:
            return Response({"suggestions": []})

        result = get_client().search(
            index=INDEX,
            size=8,
            query={
                "multi_match": {
                    "query": q,
                    "type": "bool_prefix",
                    "fields": [
                        "business_name.autocomplete",
                        "business_name.autocomplete._2gram",
                        "business_name.autocomplete._3gram",
                    ],
                }
            },
            source=["business_name", "city", "category"],
        )
        return Response({"suggestions": [{"id": hit["_id"], **hit["_source"]} for hit in result["hits"]["hits"]]})
