"""
QR Emergency Alert System - Validation Functions
Converted from: isValidIndianPhone() and cleanPhoneNumber() in server.js lines 159-171

Phone validation and cleaning utilities used during user registration.
"""

import re


def is_valid_indian_phone(phone: str) -> bool:
    """Validate phone number.

    Original: isValidIndianPhone() in server.js lines 159-162
      // Temporarily accept ANY non-empty value
      return phone && phone.trim().length > 0;

    Note: The original Node.js code accepts any non-empty string.
    This is intentionally permissive to support various phone formats.

    Args:
        phone: Phone number string to validate.

    Returns:
        True if the phone string is non-empty after trimming.
    """
    return bool(phone and phone.strip())


def clean_phone_number(phone: str) -> str:
    """Clean phone number to digits only.

    Original: cleanPhoneNumber() in server.js lines 169-171
      return phone.replace(/\\D/g, '');

    Args:
        phone: Phone number string to clean.

    Returns:
        String containing only digit characters.
    """
    return re.sub(r"\D", "", phone)
