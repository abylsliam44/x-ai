import secrets
from datetime import datetime, timezone


def generate_storage_key(prefix: str, *, extension: str) -> str:
    now = datetime.now(timezone.utc)
    rand = secrets.token_hex(6)
    ext = extension.lstrip(".")
    return f"{prefix}/{now.year:04d}/{now.month:02d}/{now.day:02d}/{rand}.{ext}"


def extension_for_mime(mime_type: str) -> str:
    mapping = {
        "image/png": "png",
        "image/jpeg": "jpg",
        "image/webp": "webp",
        "image/gif": "gif",
        "audio/mpeg": "mp3",
        "audio/wav": "wav",
        "audio/mp4": "m4a",
        "video/mp4": "mp4",
        "video/quicktime": "mov",
    }
    return mapping.get(mime_type, "bin")
