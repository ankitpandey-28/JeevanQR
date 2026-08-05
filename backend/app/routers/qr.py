from fastapi import APIRouter, Request
from fastapi.responses import Response

from app.config import settings
from app.database import get_user
from app.services.qr_service import generate_qr_png
from app.services.token_service import decode_user_token

router = APIRouter(tags=["QR Code"])

@router.get('/api/qr/{token}', summary="Generate QR code", description="Generate a QR code PNG image for the given user token. The QR code encodes the public scan URL.")
async def get_qr(token: str, request: Request):
    # Try decode from self-contained token first, then database
    user = decode_user_token(token)
    if not user:
        user = get_user(token)
    if not user:
        return Response(content='Unknown QR code', status_code=404)
    
    # Build absolute URL for QR code
    # Priority: SITE_URL > VERCEL_URL > request host > localhost:3000
    protocol = request.url.scheme or 'https'
    host = settings.SITE_URL or settings.VERCEL_URL or request.headers.get('host', 'localhost:3000')
    
    clean_host = host.replace('https://', '').replace('http://', '')
    if settings.SITE_URL:
        base_url = settings.SITE_URL if settings.SITE_URL.startswith('http') else f'https://{clean_host}'
    elif settings.VERCEL_URL:
        base_url = f'https://{settings.VERCEL_URL}'
    else:
        base_url = f'{protocol}://{clean_host}'
    
    public_url = f'{base_url}/scan/{token}'
    
    qr_buffer = generate_qr_png(public_url)
    return Response(
        content=qr_buffer,
        media_type='image/png',
        headers={'Cache-Control': 'public, max-age=31536000'}
    )
