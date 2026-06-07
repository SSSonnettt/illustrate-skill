#!/usr/bin/env python3
"""Upload image bytes to Cloudflare R2 and return public URL.

Usage:
    python3 upload-r2.py <image_path>        # 上传文件，输出 URL

Environment variables:
    R2_ACCOUNT_ID         Cloudflare Account ID
    R2_ACCESS_KEY_ID      R2 API Token Access Key
    R2_SECRET_ACCESS_KEY  R2 API Token Secret
    R2_BUCKET_NAME        R2 bucket name (default: illustrate-images)
    R2_PUBLIC_URL         Public-facing URL prefix (e.g. https://cdn.example.com)
"""

import os
import sys
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

import boto3
from botocore.config import Config


def get_env(key: str) -> str:
    value = os.environ.get(key, "")
    if not value:
        print(f"Error: ${key} is not set", file=sys.stderr)
        sys.exit(1)
    return value


def content_type_from_path(path: str) -> str:
    ext = Path(path).suffix.lower()
    mapping = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".webp": "image/webp",
        ".gif": "image/gif",
    }
    return mapping.get(ext, "image/png")


def generate_key(path: str) -> str:
    """Generate R2 object key with date-based prefix and content hash."""
    now = datetime.now()
    date_prefix = now.strftime("illustrations/%Y/%m/%d")

    # Use file content hash for dedup + short uuid for uniqueness
    with open(path, "rb") as f:
        content_hash = hashlib.md5(f.read()).hexdigest()[:8]

    short_id = str(uuid.uuid4())[:8]
    ext = Path(path).suffix or ".png"
    filename = f"{content_hash}-{short_id}{ext}"

    return f"{date_prefix}/{filename}"


def upload(path: str) -> str:
    """Upload file to R2 and return public URL."""
    account_id = get_env("R2_ACCOUNT_ID")
    access_key = get_env("R2_ACCESS_KEY_ID")
    secret_key = get_env("R2_SECRET_ACCESS_KEY")
    bucket = os.environ.get("R2_BUCKET_NAME", "illustrate-images")
    public_url = get_env("R2_PUBLIC_URL")

    s3 = boto3.client(
        "s3",
        endpoint_url=f"https://{account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        config=Config(signature_version="s3v4"),
    )

    key = generate_key(path)
    content_type = content_type_from_path(path)

    with open(path, "rb") as f:
        s3.put_object(
            Bucket=bucket,
            Key=key,
            Body=f.read(),
            ContentType=content_type,
        )

    url = f"{public_url.rstrip('/')}/{key}"
    return url


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help"):
        print(__doc__)
        sys.exit(0)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print(f"Error: file not found: {path}", file=sys.stderr)
        sys.exit(1)

    url = upload(path)
    print(url)


if __name__ == "__main__":
    main()
