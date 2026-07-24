"""
QR Emergency Alert System - Statistics Schemas
Converted from: GET /api/stats in server.js lines 417-420 and
getStats() in database.js lines 259-266

Pydantic model for the statistics endpoint.

GET /api/stats responds:
  {
    "totalUsers": 0,
    "totalAccidentLogs": 0,
    "totalPhotos": 0,
    "lastUpdated": "2024-01-01T00:00:00.000Z"
  }
"""

from pydantic import BaseModel


class StatsResponse(BaseModel):
    """Response body for GET /api/stats.

    Matches the original Node.js response from database.js getStats():
      { totalUsers, totalAccidentLogs, totalPhotos, lastUpdated }
    """
    totalUsers: int
    totalAccidentLogs: int
    totalPhotos: int
    lastUpdated: str
