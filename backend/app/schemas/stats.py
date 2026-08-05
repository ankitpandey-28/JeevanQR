"""QR Emergency Alert System - Statistics Schemas"""

from pydantic import BaseModel


class StatsResponse(BaseModel):
    """Response body for GET /api/stats."""
    totalUsers: int
    totalAccidentLogs: int
    totalPhotos: int
    lastUpdated: str
