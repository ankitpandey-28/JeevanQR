"""QR Emergency Alert System - Token Encoding/Decoding Service

Self-contained tokens encode all user data into a base64url string so that
no database lookup is needed to display emergency information. This is critical
for serverless compatibility where the in-memory database is ephemeral.

Token format (compact JSON, base64url encoded, no padding):
{
  "n": fullName,
  "b": bloodGroup,
  "e": [{"n": contactName, "p": contactPhone}, ...],
  "g": [{"n": helplineName, "p": helplineNumber}, ...],
  "t": timestampMs
}
"""

import base64
import json
import logging
import time
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


def encode_user_token(user: dict) -> str:
    """Encode user data into a self-contained base64url token.

    Args:
        user: User data dictionary with fullName, bloodGroup,
              emergencyContacts, governmentHelplines.

    Returns:
        Base64url encoded token string (no padding).
    """
    data = {
        "n": user["fullName"],
        "b": user["bloodGroup"],
        "e": [{"n": c["name"], "p": c["phone"]} for c in user["emergencyContacts"]],
        "g": [{"n": h["name"], "p": h["number"]} for h in user["governmentHelplines"]],
        "t": int(time.time() * 1000),
    }
    json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    b64 = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")
    return b64.rstrip("=")


def decode_user_token(token: str) -> dict | None:
    """Decode user data from a self-contained base64url token.

    Args:
        token: Base64url encoded token string.

    Returns:
        User data dictionary or None if decoding fails.
    """
    try:
        # Restore padding stripped during encoding
        padding_needed = 4 - (len(token) % 4)
        if padding_needed != 4:
            token += "=" * padding_needed

        json_str = base64.urlsafe_b64decode(token).decode("utf-8")
        data = json.loads(json_str)

        return {
            "fullName": data["n"],
            "bloodGroup": data["b"],
            "emergencyContacts": [
                {"name": c["n"], "phone": c["p"]} for c in data["e"]
            ],
            "governmentHelplines": [
                {"name": h["n"], "number": h["p"]} for h in data["g"]
            ],
            "createdAt": datetime.fromtimestamp(
                data["t"] / 1000, tz=timezone.utc
            ).isoformat(),
        }
    except Exception as err:
        logger.error("Failed to decode token: %s", err)
        return None
