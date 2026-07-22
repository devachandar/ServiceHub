import os
import uuid

from django.conf import settings

UPLOAD_DIR = os.path.join(settings.BASE_DIR, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def _ext(filename):
    _, ext = os.path.splitext(filename)
    return ext or ".jpg"


def save_local(file_obj):
    filename = f"{uuid.uuid4().hex}{_ext(file_obj.name)}"
    path = os.path.join(UPLOAD_DIR, filename)
    with open(path, "wb") as f:
        for chunk in file_obj.chunks():
            f.write(chunk)
    return f"/api/media/uploads/{filename}"


def save_s3(file_obj):
    import boto3

    s3 = boto3.client("s3", region_name=os.environ.get("AWS_REGION", "us-east-1"))
    key = f"servicehub/{uuid.uuid4().hex}{_ext(file_obj.name)}"
    bucket = os.environ.get("S3_BUCKET")
    s3.upload_fileobj(file_obj, bucket, key, ExtraArgs={"ContentType": file_obj.content_type})

    cdn_base = os.environ.get("CDN_BASE_URL")
    region = os.environ.get("AWS_REGION", "us-east-1")
    return f"{cdn_base}/{key}" if cdn_base else f"https://{bucket}.s3.{region}.amazonaws.com/{key}"


def save_file(file_obj):
    driver = os.environ.get("STORAGE_DRIVER", "local")
    return save_s3(file_obj) if driver == "s3" else save_local(file_obj)
