"""Module 2 Verification Script - tests all schemas and middleware components."""

import sys


def test_registration_schemas():
    """Test 1: Registration schemas match frontend JSON format."""
    print("--- Test 1: Registration Schemas ---")
    from app.schemas.registration import (
        EmergencyContact, GovernmentHelpline, RegisterRequest, RegisterResponse,
    )

    # Test EmergencyContact
    ec = EmergencyContact(name="Sunita", phone="9876543210")
    assert ec.name == "Sunita"
    assert ec.phone == "9876543210"
    print("  EmergencyContact: PASS")

    # Test GovernmentHelpline
    gh = GovernmentHelpline(name="Police", number="100")
    assert gh.name == "Police"
    assert gh.number == "100"
    print("  GovernmentHelpline: PASS")

    # Test RegisterRequest - simulate exact frontend JSON
    frontend_json = {
        "fullName": "Ravi Kumar",
        "bloodGroup": "B+",
        "emergencyContacts": [
            {"name": "Sunita", "phone": "9876543210"},
            {"name": "Amit", "phone": "9123456789"},
        ],
        "governmentHelplines": [
            {"name": "Police", "number": "100"},
            {"name": "Ambulance", "number": "108"},
        ],
    }
    req = RegisterRequest(**frontend_json)
    assert req.fullName == "Ravi Kumar"
    assert req.bloodGroup == "B+"
    assert len(req.emergencyContacts) == 2
    assert req.emergencyContacts[0].name == "Sunita"
    assert req.emergencyContacts[0].phone == "9876543210"
    assert len(req.governmentHelplines) == 2
    assert req.governmentHelplines[0].name == "Police"
    assert req.governmentHelplines[0].number == "100"
    print("  RegisterRequest (from frontend JSON): PASS")

    # Verify JSON serialization uses camelCase
    req_dict = req.model_dump()
    assert "fullName" in req_dict, "Should use camelCase 'fullName'"
    assert "bloodGroup" in req_dict, "Should use camelCase 'bloodGroup'"
    assert "emergencyContacts" in req_dict, "Should use camelCase 'emergencyContacts'"
    assert "governmentHelplines" in req_dict, "Should use camelCase 'governmentHelplines'"
    print("  camelCase field names: PASS")

    # Test RegisterResponse
    resp = RegisterResponse(
        token="abc123",
        publicUrl="/scan/abc123",
        qrImageUrl="/api/qr/abc123",
    )
    resp_dict = resp.model_dump()
    assert resp_dict["token"] == "abc123"
    assert resp_dict["publicUrl"] == "/scan/abc123"
    assert resp_dict["qrImageUrl"] == "/api/qr/abc123"
    print("  RegisterResponse: PASS")


def test_user_schemas():
    """Test 2: User schemas match original API response format."""
    print("--- Test 2: User Schemas ---")
    from app.schemas.users import (
        PublicEmergencyContact, PublicUserResponse, LocationRequest, LocationResponse,
    )
    from app.schemas.registration import GovernmentHelpline

    # Test PublicEmergencyContact - phone is base64-encoded
    pec = PublicEmergencyContact(name="Sunita", phoneEncoded="OTg3NjU0MzIxMA==")
    assert pec.name == "Sunita"
    assert pec.phoneEncoded == "OTg3NjU0MzIxMA=="
    pec_dict = pec.model_dump()
    assert "phoneEncoded" in pec_dict, "Should use camelCase 'phoneEncoded'"
    print("  PublicEmergencyContact: PASS")

    # Test PublicUserResponse - simulate exact API response
    api_response = {
        "fullName": "Ravi Kumar",
        "bloodGroup": "B+",
        "emergencyContacts": [
            {"name": "Sunita", "phoneEncoded": "OTg3NjU0MzIxMA=="},
        ],
        "governmentHelplines": [
            {"name": "Police", "number": "100"},
        ],
    }
    pub = PublicUserResponse(**api_response)
    assert pub.fullName == "Ravi Kumar"
    assert pub.bloodGroup == "B+"
    assert len(pub.emergencyContacts) == 1
    assert pub.emergencyContacts[0].phoneEncoded == "OTg3NjU0MzIxMA=="
    assert len(pub.governmentHelplines) == 1
    assert pub.governmentHelplines[0].number == "100"
    print("  PublicUserResponse: PASS")

    # Test LocationRequest - all fields optional
    loc_full = LocationRequest(latitude=28.6139, longitude=77.2090, mapsUrl="https://maps.google.com")
    assert loc_full.latitude == 28.6139
    assert loc_full.longitude == 77.2090
    assert loc_full.mapsUrl == "https://maps.google.com"
    print("  LocationRequest (full): PASS")

    loc_empty = LocationRequest()
    assert loc_empty.latitude is None
    assert loc_empty.longitude is None
    assert loc_empty.mapsUrl is None
    print("  LocationRequest (empty/optional): PASS")

    loc_partial = LocationRequest(latitude=28.6139)
    assert loc_partial.latitude == 28.6139
    assert loc_partial.longitude is None
    print("  LocationRequest (partial): PASS")

    # Test LocationResponse
    lr = LocationResponse(ok=True)
    assert lr.model_dump() == {"ok": True}
    print("  LocationResponse: PASS")


def test_photo_schemas():
    """Test 3: Photo schemas match original API response."""
    print("--- Test 3: Photo Schemas ---")
    from app.schemas.photos import PhotoUploadResponse

    resp = PhotoUploadResponse(
        success=True,
        photoUrl="/uploads/emergency-123.jpg",
        secureUrl="http://localhost:3000/photo/abc123",
        viewToken="abc123",
        message="Photo uploaded successfully",
    )
    d = resp.model_dump()
    assert d["success"] is True
    assert d["photoUrl"] == "/uploads/emergency-123.jpg"
    assert d["secureUrl"] == "http://localhost:3000/photo/abc123"
    assert d["viewToken"] == "abc123"
    assert d["message"] == "Photo uploaded successfully"

    # Verify camelCase keys
    assert "photoUrl" in d
    assert "secureUrl" in d
    assert "viewToken" in d
    print("  PhotoUploadResponse: PASS")


def test_stats_schemas():
    """Test 4: Stats schema matches database.get_stats() output."""
    print("--- Test 4: Stats Schemas ---")
    from app.schemas.stats import StatsResponse
    from app.database import get_stats

    # Verify StatsResponse can parse actual database output
    db_stats = get_stats()
    stats = StatsResponse(**db_stats)
    assert stats.totalUsers >= 0
    assert stats.totalAccidentLogs >= 0
    assert stats.totalPhotos >= 0
    assert stats.lastUpdated != ""

    # Verify camelCase keys
    d = stats.model_dump()
    assert "totalUsers" in d
    assert "totalAccidentLogs" in d
    assert "totalPhotos" in d
    assert "lastUpdated" in d
    print("  StatsResponse from get_stats(): PASS")


def test_error_handler():
    """Test 5: Error handler functions are importable and callable."""
    print("--- Test 5: Error Handler ---")
    from app.middleware.error_handler import http_exception_handler, generic_exception_handler
    import asyncio

    # Test HTTP exception handler
    from starlette.exceptions import HTTPException as StarletteHTTPException
    from starlette.testclient import TestClient

    exc_404 = StarletteHTTPException(status_code=404)
    resp_404 = asyncio.run(http_exception_handler(None, exc_404))
    assert resp_404.status_code == 404
    assert resp_404.body == b"Page not found"
    print("  http_exception_handler (404): PASS")

    exc_400 = StarletteHTTPException(status_code=400, detail="Bad request")
    resp_400 = asyncio.run(http_exception_handler(None, exc_400))
    assert resp_400.status_code == 400
    assert resp_400.body == b"Bad request"
    print("  http_exception_handler (400): PASS")

    # Test generic exception handler
    exc_generic = Exception("Something broke")
    resp_500 = asyncio.run(generic_exception_handler(None, exc_generic))
    assert resp_500.status_code == 500
    assert resp_500.body == b"Internal server error"
    print("  generic_exception_handler (500): PASS")


def test_cross_module_compatibility():
    """Test 6: Schemas work with Module 1 services."""
    print("--- Test 6: Cross-Module Compatibility ---")
    from app.schemas.registration import RegisterRequest, EmergencyContact, GovernmentHelpline
    from app.services.token_service import encode_user_token, decode_user_token
    from app.services.validation import is_valid_indian_phone, clean_phone_number
    from app.utils.helpers import encode_base64

    # Build a request object like the frontend sends
    req = RegisterRequest(
        fullName="Ravi Kumar",
        bloodGroup="B+",
        emergencyContacts=[EmergencyContact(name="Sunita", phone="9876543210")],
        governmentHelplines=[GovernmentHelpline(name="Police", number="100")],
    )

    # Validate contacts (as routers would)
    for c in req.emergencyContacts:
        assert is_valid_indian_phone(c.phone)
    for h in req.governmentHelplines:
        assert is_valid_indian_phone(h.number)
    print("  Validation with schema objects: PASS")

    # Build user dict and encode token (as registration router would)
    user = {
        "fullName": req.fullName.strip(),
        "bloodGroup": req.bloodGroup.strip().upper(),
        "emergencyContacts": [
            {"name": c.name.strip(), "phone": clean_phone_number(c.phone)}
            for c in req.emergencyContacts
        ],
        "governmentHelplines": [
            {"name": h.name.strip(), "number": clean_phone_number(h.number)}
            for h in req.governmentHelplines
        ],
    }
    token = encode_user_token(user)
    assert token is not None
    print("  Token from schema data: PASS")

    # Decode and build public response (as users router would)
    decoded = decode_user_token(token)
    public_contacts = [
        {"name": c["name"], "phoneEncoded": encode_base64(c["phone"])}
        for c in decoded["emergencyContacts"]
    ]
    assert public_contacts[0]["name"] == "Sunita"
    assert public_contacts[0]["phoneEncoded"] == "OTg3NjU0MzIxMA=="

    from app.schemas.users import PublicUserResponse, PublicEmergencyContact
    pub = PublicUserResponse(
        fullName=decoded["fullName"],
        bloodGroup=decoded["bloodGroup"],
        emergencyContacts=[PublicEmergencyContact(**c) for c in public_contacts],
        governmentHelplines=[GovernmentHelpline(**h) for h in decoded["governmentHelplines"]],
    )
    assert pub.fullName == "Ravi Kumar"
    print("  Full registration-to-public pipeline: PASS")


def test_no_circular_imports():
    """Test 7: No circular imports across Modules 1 and 2."""
    print("--- Test 7: Circular Import Check ---")
    from app.config import settings
    from app.database import save_user, get_user, get_stats
    from app.services.token_service import encode_user_token, decode_user_token
    from app.services.qr_service import generate_qr_png
    from app.services.validation import is_valid_indian_phone, clean_phone_number
    from app.utils.helpers import generate_token, encode_base64
    from app.schemas.registration import RegisterRequest, RegisterResponse
    from app.schemas.users import PublicUserResponse, LocationRequest, LocationResponse
    from app.schemas.photos import PhotoUploadResponse
    from app.schemas.stats import StatsResponse
    from app.middleware.error_handler import http_exception_handler, generic_exception_handler
    print("  All Module 1+2 imports together: PASS")


if __name__ == "__main__":
    passed = 0
    failed = 0
    errors = []

    tests = [
        test_registration_schemas,
        test_user_schemas,
        test_photo_schemas,
        test_stats_schemas,
        test_error_handler,
        test_cross_module_compatibility,
        test_no_circular_imports,
    ]

    for test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            failed += 1
            errors.append((test_fn.__name__, str(e)))
            print(f"  FAILED: {e}")

    print()
    print("=" * 50)
    print(f"  Module 2 Verification: {passed}/{passed + failed} tests passed")
    if errors:
        print("  FAILURES:")
        for name, err in errors:
            print(f"    {name}: {err}")
        sys.exit(1)
    else:
        print("  ALL TESTS PASSED!")
    print("=" * 50)
