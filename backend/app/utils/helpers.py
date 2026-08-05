"""QR Emergency Alert System - Utility Helpers

General-purpose utility functions used across the application.
"""

import base64
import secrets


def generate_token() -> str:
    """Generate a secure random 32-character hex token.

    Returns:
        32-character lowercase hex string.
    """
    return secrets.token_hex(16)


def encode_base64(s: str) -> str:
    """Encode a string to base64.

    Used to encode phone numbers before sending them to the frontend.
    The frontend decodes them for tel: links.

    Args:
        s: String to encode.

    Returns:
        Base64 encoded string.
    """
    return base64.b64encode(s.encode("utf-8")).decode("utf-8")
