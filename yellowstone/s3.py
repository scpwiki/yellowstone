"""
Utilities for interacting with the S3 bucket where Wikidot files are being kept.
"""

import hashlib
import logging
import os

import boto3
from botocore.exceptions import ClientError

from .config import Config, getenv

AVATAR_DIRECTORY = "avatars"
FILE_DIRECTORY = "files"

logger = logging.getLogger(__name__)


class S3:
    __slots__ = (
        "bucket",
        "client",
    )

    bucket: str

    def __init__(self, config: Config) -> None:
        self.bucket = config.s3_bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=getenv("S3_ACCESS_KEY"),
            aws_secret_access_key=getenv("S3_SECRET_KEY"),
        )

    def upload_avatar(self, blob: bytes) -> bytes:
        return self.upload_blob(blob, AVATAR_DIRECTORY)

    def upload_file(self, blob: bytes) -> bytes:
        return self.upload_blob(blob, FILE_DIRECTORY)

    def upload_blob(self, blob: bytes, directory: str) -> bytes:
        blob_hash = hashlib.sha512(blob)
        hex_hash = blob_hash.hexdigest()
        path = os.path.join(directory, hex_hash)
        logger.debug("Want to persist blob to S3 (hash %s)", hex_hash)

        # Only upload if not present
        if not self.object_exists(path):
            logger.info(
                "Uploading S3 blob (directory %s, hash %s, length %d)",
                directory,
                hex_hash,
                len(blob),
            )
            self.client.put_object(
                Bucket=self.bucket,
                Key=path,
                Body=blob,
            )

        # Return object hash
        return blob_hash.digest()

    def object_exists(self, path) -> bool:
        logging.debug("Checking if S3 path '%s' exists", path)
        try:
            self.client.head_object(
                Bucket=self.bucket,
                Key=path,
            )
            return True
        except ClientError:
            return False
