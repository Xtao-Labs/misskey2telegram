from io import BytesIO
from PIL import Image


def webp_to_jpg(content: bytes) -> BytesIO:
    """Convert a WebP image to a JPEG image."""
    im = Image.open(BytesIO(content))
    jpg = BytesIO()
    rgb_im = im.convert("RGB")
    rgb_im.save(jpg, "JPEG")
    jpg.seek(0)
    return jpg
