from datetime import datetime, timezone
import time as time_mod
import random
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import FileResponse, JSONResponse, Response
from backend.app.database import get_user, log_photo_upload, get_photo_by_view_token, mark_photo_as_viewed
from backend.app.utils.helpers import generate_token
from backend.app.config import settings

router = APIRouter()

@router.post('/api/upload-photo')
async def upload_photo(
    request: Request,
    photo: UploadFile = File(...),
    token: str = Form(...),
    patientName: str = Form(default=''),
    timestamp: str = Form(default='')
):
    # Validate user exists (database only, not token-decode, matching original)
    user = get_user(token)
    if not user:
        return JSONResponse(content={'error': 'User not found'}, status_code=404)
    
    if not photo:
        return JSONResponse(content={'error': 'No photo uploaded'}, status_code=400)
    
    # Check file is image
    if not photo.content_type or not photo.content_type.startswith('image/'):
        return JSONResponse(content={'error': 'Only image files are allowed'}, status_code=400)
    
    # Check file size (5MB limit)
    contents = await photo.read()
    if len(contents) > 5 * 1024 * 1024:
        return JSONResponse(content={'error': 'File too large. Maximum 5MB.'}, status_code=400)
    
    # Generate unique filename
    unique_suffix = f"{int(time_mod.time() * 1000)}-{random.randint(0, 999999999)}"
    filename = f"emergency-{unique_suffix}.jpg"
    
    # Save file to uploads directory
    if not settings.is_serverless:
        settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
        filepath = settings.UPLOADS_DIR / filename
        with open(filepath, 'wb') as f:
            f.write(contents)
    
    # Generate secure view token
    view_token = generate_token()
    
    # Log photo upload
    log_photo_upload(token, {
        'filename': filename,
        'originalName': photo.filename,
        'size': len(contents),
        'patientName': patientName,
        'timestamp': timestamp,
        'uploadedAt': datetime.now(timezone.utc).isoformat(),
        'viewToken': view_token
    })
    
    photo_url = f'/uploads/{filename}'
    protocol = request.url.scheme
    host = request.headers.get('host', 'localhost:3000')
    secure_url = f'{protocol}://{host}/photo/{view_token}'
    
    return {
        'success': True,
        'photoUrl': photo_url,
        'secureUrl': secure_url,
        'viewToken': view_token,
        'message': 'Photo uploaded successfully'
    }

@router.get('/photo/{view_token}')
async def view_photo(view_token: str):
    photo_info = get_photo_by_view_token(view_token)
    if not photo_info:
        return Response(content='Photo not found or expired', status_code=404)
    
    if photo_info.get('viewed'):
        return Response(content='Photo link expired - one-time access only', status_code=410)
    
    mark_photo_as_viewed(view_token)
    
    return FileResponse(settings.FRONTEND_DIR / 'photo-view.html')
