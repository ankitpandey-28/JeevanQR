"""
QR Emergency Alert System - Token Encoding/Decoding Service
Converted from: encodeUserToken() and decodeUserToken() in server.js lines 122-152

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

Node.js compatibility:
  - Uses base64url encoding (urlsafe alphabet, no = padding)
  - JSON uses compact separators (',', ':') to minimize token length
  - Timestamp is milliseconds since epoch (matching JS Date.now())
"""

import base64
import json
import logging
import time
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)


def encode_user_token(user: dict) -> str:
    """Encode user data into a self-contained base64url token.

    Original: encodeUserToken() in server.js lines 122-131
      const data = {
        n: user.fullName,
        b: user.bloodGroup,
        e: user.emergencyContacts.map(c => ({ n: c.name, p: c.phone })),
        g: user.governmentHelplines.map(h => ({ n: h.name, p: h.number })),
        t: Date.now()
      };
      return Buffer.from(JSON.stringify(data), 'utf8').toString('base64url');

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
        "t": int(time.time() * 1000),  # milliseconds, matching JS Date.now()
    }
    json_str = json.dumps(data, separators=(",", ":"), ensure_ascii=False)
    # base64url encode and strip = padding to match Node.js base64url
    b64 = base64.urlsafe_b64encode(json_str.encode("utf-8")).decode("utf-8")
    return b64.rstrip("=")


def decode_user_token(token: str) -> Optional[dict]:
    """Decode user data from a self-contained base64url token.

    Original: decodeUserToken() in server.js lines 138-152
      const data = JSON.parse(Buffer.from(token, 'base64url').toString('utf8'));
      return {
        fullName: data.n,
        bloodGroup: data.b,
        emergencyContacts: data.e.map(c => ({ name: c.n, phone: c.p })),
        governmentHelplines: data.g.map(h => ({ name: h.n, number: h.p })),
        createdAt: new Date(data.t).toISOString()
      };

    Args:
        token: Base64url encoded token string.

    Returns:
        User data dictionary or None if decoding fails.
    """
    try:
        # Add back = padding that was stripped during encoding
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
