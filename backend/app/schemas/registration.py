"""
QR Emergency Alert System - Registration Schemas
Converted from: POST /api/register in server.js lines 224-296

Pydantic models for the user registration endpoint.
Field names use camelCase to match the frontend JSON format exactly.

Frontend sends (from government-helplines.js):
  POST /api/register
  {
    "fullName": "Ravi Kumar",
    "bloodGroup": "B+",
    "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
    "governmentHelplines": [{"name": "Police", "number": "100"}]
  }

Backend responds:
  {
    "token": "<base64url string>",
    "publicUrl": "/scan/<token>",
    "qrImageUrl": "/api/qr/<token>"
  }
"""

from pydantic import BaseModel
from typing import List


class EmergencyContact(BaseModel):
    """Emergency contact with name and phone number.

    Matches the frontend contact object:
      { name: contact.name.trim(), phone: contact.phone }
    """
    name: str
    phone: str


class GovernmentHelpline(BaseModel):
    """Government helpline with name and number.

    Matches the frontend helpline object:
      { name: helpline.name.trim(), number: helpline.number }

    Note: uses 'number' (not 'phone') to match the original Node.js schema.
    """
    name: str
    number: str


class RegisterRequest(BaseModel):
    """Request body for POST /api/register.

    All fields use camelCase to match the frontend JSON keys exactly.
    The frontend builds this in government-helplines.js submitRegistration().

    Fields default to empty strings / empty lists so that FastAPI accepts
    partial payloads and custom validation in the router produces the same
    400 error messages as the original Node.js backend.
    """
    fullName: str = ""
    bloodGroup: str = ""
    emergencyContacts: List[EmergencyContact] = []
    governmentHelplines: List[GovernmentHelpline] = []


class RegisterResponse(BaseModel):
    """Response body for POST /api/register.

    Matches the original Node.js response:
      res.json({ token, publicUrl, qrImageUrl })
    """
    token: str
    publicUrl: str
    qrImageUrl: str
