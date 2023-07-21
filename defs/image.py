from io import BytesIO
from PIL import Image


def webp_to_png(content: bytes) -> BytesIO:
    """Convert a WebP image to a PNG image."""
    im = Image.open(BytesIO(content))
    jpg = BytesIO()
    im.save(jpg, "JPEG")
    jpg.seek(0)
    return jpg
