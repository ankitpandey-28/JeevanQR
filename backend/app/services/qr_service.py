"""
QR Emergency Alert System - QR Code Generation Service
Converted from: QRCode.toBuffer() calls in server.js lines 338-343

Uses the `qrcode` Python library with Pillow backend to generate
QR code PNG images, matching the Node.js `qrcode` npm package behavior.

Node.js equivalent:
  QRCode.toBuffer(url, { errorCorrectionLevel: 'M', margin: 1, width: 512 })
"""

import qrcode
from io import BytesIO
from PIL import Image


def generate_qr_png(data: str, size: int = 512) -> bytes:
    """Generate a QR code as a PNG byte buffer.

    Args:
        data: The string data to encode in the QR code (typically a URL).
        size: Output image size in pixels (square). Default 512 to match Node.js.

    Returns:
        PNG image as bytes.
    """
    qr = qrcode.QRCode(
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=1,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Generate PIL image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to PIL.Image if needed and resize to exact target size
    if not isinstance(img, Image.Image):
        img = img.get_image()
    img = img.resize((size, size), Image.LANCZOS)

    # Write PNG to buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
