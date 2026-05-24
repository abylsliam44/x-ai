from app.core.config import settings
from app.core.exceptions import ValidationError


def assert_image_mime(mime_type: str) -> None:
    if mime_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
        raise ValidationError(f"Image mime type {mime_type} is not allowed")


def assert_video_mime(mime_type: str) -> None:
    if mime_type not in settings.ALLOWED_VIDEO_MIME_TYPES:
        raise ValidationError(f"Video mime type {mime_type} is not allowed")


def assert_audio_mime(mime_type: str) -> None:
    if mime_type not in settings.ALLOWED_AUDIO_MIME_TYPES:
        raise ValidationError(f"Audio mime type {mime_type} is not allowed")


def assert_within_max_upload(size_bytes: int) -> None:
    max_bytes = settings.MAX_UPLOAD_SIZE_MB * 1024 * 1024
    if size_bytes > max_bytes:
        raise ValidationError(f"File too large: {size_bytes} bytes; max {max_bytes}")


def assert_max_images_per_post(count: int) -> None:
    if count > settings.MAX_IMAGES_PER_POST:
        raise ValidationError(
            f"Too many images: {count}; max {settings.MAX_IMAGES_PER_POST} per post"
        )
