from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsAuthenticatedStateless
from .storage import UPLOAD_DIR, save_file

ALLOWED_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_SIZE = 8 * 1024 * 1024
MAX_FILES = 10


class UploadView(APIView):
    permission_classes = [IsAuthenticatedStateless]
    parser_classes = [MultiPartParser]

    def post(self, request):
        files = request.FILES.getlist("images")
        if not files:
            return Response({"error": "No files were provided under the 'images' field"}, status=400)
        if len(files) > MAX_FILES:
            return Response({"error": f"You can upload at most {MAX_FILES} files at once"}, status=400)

        urls = []
        for f in files:
            if f.content_type not in ALLOWED_TYPES:
                return Response({"error": f"Unsupported file type: {f.content_type}"}, status=400)
            if f.size > MAX_SIZE:
                return Response({"error": f"{f.name} is larger than 8MB"}, status=400)
            urls.append(save_file(f))

        return Response({"urls": urls}, status=201)


class ServeUploadView(APIView):
    """Only used with STORAGE_DRIVER=local - serves files from disk so the
    project runs with zero cloud setup. In front of an S3 driver this route
    is simply unused since URLs point straight at S3/CloudFront."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, filename):
        import os

        path = os.path.join(UPLOAD_DIR, filename)
        if not os.path.isfile(path):
            raise Http404
        return FileResponse(open(path, "rb"))
