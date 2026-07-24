"""
QR Emergency Alert System - Photo Upload Schemas
Converted from: POST /api/upload-photo in server.js lines 426-469

Pydantic models for the photo upload endpoint.

POST /api/upload-photo responds:
  {
    "success": true,
    "photoUrl": "/uploads/emergency-<id>.jpg",
    "secureUrl": "http://host/photo/<viewToken>",
    "viewToken": "<hex string>",
    "message": "Photo uploaded successfully"
  }
"""

from pydantic import BaseModel


class PhotoUploadResponse(BaseModel):
    """Response body for POST /api/upload-photo.

    Matches the original Node.js response in server.js lines 458-464.
    """
    success: bool
    photoUrl: str
    secureUrl: str
    viewToken: str
    message: str
