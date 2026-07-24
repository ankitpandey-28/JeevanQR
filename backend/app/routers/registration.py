from datetime import datetime, timezone
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.app.database import save_user
from backend.app.services.token_service import encode_user_token
from backend.app.services.validation import is_valid_indian_phone, clean_phone_number
from backend.app.schemas.registration import RegisterRequest

router = APIRouter()

@router.post('/api/register')
async def register(request: RegisterRequest):
    # Validate required fields
    if not request.fullName or not request.bloodGroup:
        return JSONResponse(content={'error': 'Missing required fields. सभी जानकारी आवश्यक है।'}, status_code=400)
    
    # Validate emergency contacts (must be non-empty list)
    if not request.emergencyContacts or len(request.emergencyContacts) == 0:
        return JSONResponse(content={'error': 'At least one emergency contact is required. कम से कम एक आपातकालीन संपर्क आवश्यक है।'}, status_code=400)
    
    # Validate government helplines (must be non-empty list)
    if not request.governmentHelplines or len(request.governmentHelplines) == 0:
        return JSONResponse(content={'error': 'At least one government helpline is required. कम से कम एक सरकारी हेल्पलाइन आवश्यक है।'}, status_code=400)
    
    # Validate each emergency contact
    for contact in request.emergencyContacts:
        if not contact.name or not contact.phone or not is_valid_indian_phone(contact.phone):
            return JSONResponse(content={'error': 'Invalid emergency contact information. अमान्य आपातकालीन संपर्क जानकारी।'}, status_code=400)
    
    # Validate each government helpline
    for helpline in request.governmentHelplines:
        if not helpline.name or not helpline.number or not is_valid_indian_phone(helpline.number):
            return JSONResponse(content={'error': 'Invalid government helpline information. अमान्य सरकारी हेल्पलाइन जानकारी।'}, status_code=400)
    
    # Create user record
    user = {
        'fullName': request.fullName.strip(),
        'bloodGroup': request.bloodGroup.strip().upper(),
        'emergencyContacts': [{'name': c.name.strip(), 'phone': clean_phone_number(c.phone)} for c in request.emergencyContacts],
        'governmentHelplines': [{'name': h.name.strip(), 'number': clean_phone_number(h.number)} for h in request.governmentHelplines],
        'createdAt': datetime.now(timezone.utc).isoformat()
    }
    
    token = encode_user_token(user)
    save_user(token, user)
    
    return {'token': token, 'publicUrl': f'/scan/{token}', 'qrImageUrl': f'/api/qr/{token}'}
