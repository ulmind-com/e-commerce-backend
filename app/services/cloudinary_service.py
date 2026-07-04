import cloudinary
import cloudinary.uploader
import cloudinary.api
from app.core.config import settings

_configured = False


def _ensure_configured():
    """Lazily configure Cloudinary once using env settings."""
    global _configured
    if not _configured:
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET,
            secure=True,
        )
        _configured = True


def upload_image(file_content, folder: str = "ecommerce/products", public_id: str = None) -> str | None:
    """
    Upload a file-like object to Cloudinary.
    Returns the secure HTTPS URL or None on failure.
    """
    _ensure_configured()
    try:
        kwargs = {
            "folder": folder,
            "resource_type": "image",
            "overwrite": True,
            "quality": "auto",
            "fetch_format": "auto",
        }
        if public_id:
            kwargs["public_id"] = public_id

        response = cloudinary.uploader.upload(file_content, **kwargs)
        return response.get("secure_url")
    except Exception as e:
        print(f"[Cloudinary] Upload error: {e}")
        return None


def upload_avatar(file_content, user_id: str) -> str | None:
    """Upload a user profile avatar to a dedicated folder."""
    _ensure_configured()
    try:
        response = cloudinary.uploader.upload(
            file_content,
            folder="ecommerce/avatars",
            public_id=f"user_{user_id}",
            overwrite=True,
            resource_type="image",
            transformation=[
                {"width": 400, "height": 400, "crop": "fill", "gravity": "face"},
                {"quality": "auto", "fetch_format": "auto"},
            ],
        )
        return response.get("secure_url")
    except Exception as e:
        print(f"[Cloudinary] Avatar upload error: {e}")
        return None


def delete_image(public_id: str) -> bool:
    """
    Delete an image from Cloudinary by its public_id.
    Returns True on success, False otherwise.
    """
    _ensure_configured()
    try:
        result = cloudinary.uploader.destroy(public_id, resource_type="image")
        return result.get("result") == "ok"
    except Exception as e:
        print(f"[Cloudinary] Delete error: {e}")
        return False


def get_public_id_from_url(url: str) -> str | None:
    """
    Extract the Cloudinary public_id from a secure URL.
    e.g. .../ecommerce/products/abc123.jpg  →  ecommerce/products/abc123
    """
    try:
        # Strip query params and extension
        path = url.split("/upload/")[-1]
        # Remove version segment like v1234567890/
        parts = path.split("/")
        if parts[0].startswith("v") and parts[0][1:].isdigit():
            parts = parts[1:]
        public_id_with_ext = "/".join(parts)
        public_id = ".".join(public_id_with_ext.split(".")[:-1])
        return public_id
    except Exception:
        return None
