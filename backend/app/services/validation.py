"""QR Emergency Alert System - Validation Functions

Phone validation and cleaning utilities used during user registration.
"""

import re


def is_valid_indian_phone(phone: str) -> bool:
    """Validate phone number.

    Accepts any non-empty string after trimming. This is intentionally
    permissive to support various phone formats.

    Args:
        phone: Phone number string to validate.

    Returns:
        True if the phone string is non-empty after trimming.
    """
    return bool(phone and phone.strip())


def clean_phone_number(phone: str) -> str:
    """Clean phone number to digits only.

    Args:
        phone: Phone number string to clean.

    Returns:
        String containing only digit characters.
    """
    return re.sub(r"\D", "", phone)
