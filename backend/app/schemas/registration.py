"""QR Emergency Alert System - Registration Schemas

Pydantic models for the user registration endpoint.
Field names use camelCase to match the frontend JSON format.
"""

from pydantic import BaseModel


class EmergencyContact(BaseModel):
    """Emergency contact with name and phone number."""
    name: str
    phone: str


class GovernmentHelpline(BaseModel):
    """Government helpline with name and number."""
    name: str
    number: str


class RegisterRequest(BaseModel):
    """Request body for POST /api/register.

    All fields use camelCase to match the frontend JSON keys.
    Fields default to empty strings / empty lists so that partial
    payloads are accepted and custom validation in the router
    produces the appropriate 400 error messages.
    """
    fullName: str = ""
    bloodGroup: str = ""
    emergencyContacts: list[EmergencyContact] = []
    governmentHelplines: list[GovernmentHelpline] = []


class RegisterResponse(BaseModel):
    """Response body for POST /api/register."""
    token: str
    publicUrl: str
    qrImageUrl: str
