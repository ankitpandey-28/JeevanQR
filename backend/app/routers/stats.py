from fastapi import APIRouter

from app.database import get_stats as db_get_stats

router = APIRouter(tags=["Statistics"])

@router.get('/api/stats', summary="Get statistics", description="Get database statistics including total users, accident logs, photos, and last update timestamp.")
async def stats():
    return db_get_stats()
