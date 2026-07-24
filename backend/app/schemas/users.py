"""
QR Emergency Alert System - User Endpoint Schemas
Converted from: GET /api/users/:token/public and POST /api/users/:token/location
in server.js lines 354-411

Pydantic models for user data retrieval and location logging.

GET /api/users/{token}/public responds:
  {
    "fullName": "Ravi Kumar",
    "bloodGroup": "B+",
    "emergencyContacts": [{"name": "Sunita", "phoneEncoded": "<base64>"}],
    "governmentHelplines": [{"name": "Police", "number": "100"}]
  }

POST /api/users/{token}/location receives:
  { "latitude": 28.6139, "longitude": 77.2090, "mapsUrl": "https://..." }
and responds:
  { "ok": true }
"""

from pydantic import BaseModel
from typing import List, Optional

from backend.app.schemas.registration import GovernmentHelpline


class PublicEmergencyContact(BaseModel):
    """Emergency contact with base64-encoded phone number.

    The phone number is NOT sent as plain text. It is base64-encoded
    so that the frontend can decode it with atob() and create tel: links
    without exposing the number as visible text on the page.

    Matches the original Node.js response:
      emergencyContacts.map(contact => ({
        name: contact.name,
        phoneEncoded: encodeBase64(contact.phone)
      }))
    """
    name: str
    phoneEncoded: str


class PublicUserResponse(BaseModel):
    """Response body for GET /api/users/{token}/public.

    Matches the original Node.js response in server.js lines 370-378.
    """
    fullName: str
    bloodGroup: str
    emergencyContacts: List[PublicEmergencyContact]
    governmentHelplines: List[GovernmentHelpline]


class LocationRequest(BaseModel):
    """Request body for POST /api/users/{token}/location.

    All fields are optional because the frontend sends whatever
    geolocation data is available. From scan.js logLocationToBackend():
      { latitude, longitude, mapsUrl }

    Matches the original Node.js:
      const { latitude, longitude, mapsUrl } = req.body || {};
    """
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    mapsUrl: Optional[str] = None


class LocationResponse(BaseModel):
    """Response body for POST /api/users/{token}/location.

    Matches the original Node.js: res.json({ ok: true })
    """
    ok: bool
