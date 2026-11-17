"""Product photos in the Supabase Storage bucket "product-images" (0006). Owner: User 3.

Rules (NFR-SEC-06): PNG or JPG only, checked by extension AND file signature; 2 MB max; random file name.
"""

from __future__ import annotations

MAX_IMAGE_BYTES = 2 * 1024 * 1024
BUCKET = "product-images"


def upload_image(file_name: str, data: bytes) -> str:
    """Uploads a product photo and returns its public URL (US-MGT-07, U3-05)."""
    raise NotImplementedError("US-MGT-07: upload_image (U3-05)")
