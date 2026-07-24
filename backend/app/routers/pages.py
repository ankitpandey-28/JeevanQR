from fastapi import APIRouter
from fastapi.responses import FileResponse
from backend.app.config import settings

router = APIRouter()

@router.get('/', include_in_schema=False)
async def index():
    return FileResponse(settings.FRONTEND_DIR / 'index.html')

@router.get('/qr.html', include_in_schema=False)
async def qr_page():
    return FileResponse(settings.FRONTEND_DIR / 'qr.html')

@router.get('/emergency-contacts.html', include_in_schema=False)
async def emergency_contacts_page():
    return FileResponse(settings.FRONTEND_DIR / 'emergency-contacts.html')

@router.get('/government-helplines.html', include_in_schema=False)
async def government_helplines_page():
    return FileResponse(settings.FRONTEND_DIR / 'government-helplines.html')

@router.get('/privacy-settings.html', include_in_schema=False)
async def privacy_settings_page():
    return FileResponse(settings.FRONTEND_DIR / 'privacy-settings.html')

@router.get('/scan/{token}', include_in_schema=False)
async def scan_page(token: str):
    return FileResponse(settings.FRONTEND_DIR / 'scan.html')
