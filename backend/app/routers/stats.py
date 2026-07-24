from fastapi import APIRouter
from backend.app.database import get_stats as db_get_stats

router = APIRouter()

@router.get('/api/stats')
async def stats():
    return db_get_stats()
