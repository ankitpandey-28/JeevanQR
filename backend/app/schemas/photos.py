"""QR Emergency Alert System - Photo Upload Schemas"""

from pydantic import BaseModel


class PhotoUploadResponse(BaseModel):
    """Response body for POST /api/upload-photo."""
    success: bool
    photoUrl: str
    secureUrl: str
    viewToken: str
    message: str
