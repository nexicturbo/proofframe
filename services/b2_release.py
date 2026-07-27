"""Backblaze B2 release sink for ProofFrame Genblaze runs."""

from __future__ import annotations

import os

from genblaze_core import KeyStrategy, ObjectStorageSink
from genblaze_s3 import S3StorageBackend


def create_b2_sink() -> ObjectStorageSink | None:
    """Return a content-addressed B2 sink when all required settings exist.

    Genblaze reads the credentials directly from the environment. Returning
    ``None`` keeps local fixture runs usable without silently pretending that
    an upload occurred.
    """

    bucket = os.getenv("B2_BUCKET")
    key_id = os.getenv("B2_KEY_ID")
    app_key = os.getenv("B2_APP_KEY")
    if not all((bucket, key_id, app_key)):
        return None

    region = os.getenv("B2_REGION", "us-west-004")
    public_url_base = os.getenv("B2_PUBLIC_URL_BASE")
    backend = S3StorageBackend.for_backblaze(
        bucket,
        key_id=key_id,
        app_key=app_key,
        region=region,
        public_url_base=public_url_base,
        auto_lifecycle=False,
    )
    return ObjectStorageSink(
        backend,
        prefix="proofframe",
        key_strategy=KeyStrategy.CONTENT_ADDRESSABLE,
    )
