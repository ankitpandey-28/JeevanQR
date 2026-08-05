"""QR Emergency Alert System - User Endpoint Schemas

Pydantic models for user data retrieval and location logging.
"""

from pydantic import BaseModel

from app.schemas.registration import GovernmentHelpline


class PublicEmergencyContact(BaseModel):
    """Emergency contact with base64-encoded phone number.

    The phone number is base64-encoded so that the frontend can
    decode it and create tel: links without exposing the number
    as visible text on the page.
    """
    name: str
    phoneEncoded: str


class PublicUserResponse(BaseModel):
    """Response body for GET /api/users/{token}/public."""
    fullName: str
    bloodGroup: str
    emergencyContacts: list[PublicEmergencyContact]
    governmentHelplines: list[GovernmentHelpline]


class LocationRequest(BaseModel):
    """Request body for POST /api/users/{token}/location.

    All fields are optional because the frontend sends whatever
    geolocation data is available.
    """
    latitude: float | None = None
    longitude: float | None = None
    mapsUrl: str | None = None


class LocationResponse(BaseModel):
    """Response body for POST /api/users/{token}/location."""
    ok: bool
