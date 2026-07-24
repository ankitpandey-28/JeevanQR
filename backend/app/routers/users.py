from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.app.database import get_user, log_accident_location
from backend.app.services.token_service import decode_user_token
from backend.app.utils.helpers import encode_base64
from backend.app.schemas.users import LocationRequest

router = APIRouter()

@router.get('/api/users/{token}/public')
async def get_public_user(token: str):
    user = decode_user_token(token)
    if not user:
        user = get_user(token)
    if not user:
        return JSONResponse(content={'error': 'User not found'}, status_code=404)
    
    return {
        'fullName': user['fullName'],
        'bloodGroup': user['bloodGroup'],
        'emergencyContacts': [
            {'name': c['name'], 'phoneEncoded': encode_base64(c['phone'])}
            for c in user['emergencyContacts']
        ],
        'governmentHelplines': user.get('governmentHelplines', [])
    }

@router.post('/api/users/{token}/location')
async def post_location(token: str, body: LocationRequest):
    user = decode_user_token(token)
    if not user:
        user = get_user(token)
    if not user:
        return JSONResponse(content={'error': 'User not found'}, status_code=404)
    
    log_accident_location(token, {
        'userName': user['fullName'],
        'latitude': body.latitude,
        'longitude': body.longitude,
        'mapsUrl': body.mapsUrl,
        'reportedAt': datetime.now(timezone.utc).isoformat()
    })
    
    return {'ok': True}
