"""Module 1 Verification Script — tests all foundation components."""

import sys

def test_config():
    """Test 1: Config imports and properties."""
    print("--- Test 1: Config ---")
    from app.config import settings

    assert settings.PORT == 3000, f"PORT should be 3000, got {settings.PORT}"
    assert settings.is_serverless is False, "Should not be serverless locally"
    assert settings.FRONTEND_DIR.name == "frontend"
    assert settings.DATABASE_DIR.name == "database"
    assert settings.UPLOADS_DIR.name == "uploads"
    assert settings.ENVIRONMENT == "development"
    assert settings.ALLOWED_ORIGIN is None
    assert settings.SITE_URL is None
    print("  All config properties: PASS")


def test_database():
    """Test 2: Database CRUD operations."""
    print("--- Test 2: Database ---")
    from app.database import (
        save_user, get_user, get_all_users, delete_user,
        log_accident_location, get_recent_accident_logs,
        log_photo_upload, get_photo_by_view_token, mark_photo_as_viewed,
        get_stats,
    )

    # Test stats keys match Node.js format
    stats = get_stats()
    assert "totalUsers" in stats, "Missing totalUsers key"
    assert "totalAccidentLogs" in stats, "Missing totalAccidentLogs key"
    assert "totalPhotos" in stats, "Missing totalPhotos key"
    assert "lastUpdated" in stats, "Missing lastUpdated key"
    print("  Stats keys match Node.js: PASS")

    # Test user CRUD
    save_user("test_token_abc", {
        "fullName": "Test User",
        "bloodGroup": "O+",
        "emergencyContacts": [{"name": "Mom", "phone": "9876543210"}],
        "governmentHelplines": [{"name": "Police", "number": "100"}],
    })
    user = get_user("test_token_abc")
    assert user is not None, "save_user/get_user failed"
    assert user["fullName"] == "Test User"
    print("  save_user / get_user: PASS")

    all_users = get_all_users()
    assert "test_token_abc" in all_users
    print("  get_all_users: PASS")

    assert delete_user("test_token_abc") is True
    assert get_user("test_token_abc") is None
    assert delete_user("nonexistent") is False
    print("  delete_user: PASS")

    # Test accident logs
    log_accident_location("tok123", {
        "userName": "Ravi",
        "latitude": 28.6139,
        "longitude": 77.2090,
        "mapsUrl": "https://maps.google.com/?q=28.6139,77.2090",
        "reportedAt": "2024-01-01T00:00:00Z",
    })
    logs = get_recent_accident_logs(5)
    assert len(logs) >= 1
    assert "id" in logs[0], "Accident log should have 'id' field (flat structure)"
    assert "token" in logs[0], "Accident log should have 'token' field"
    assert "userName" in logs[0], "Accident log should have 'userName' field (flat)"
    print("  log_accident_location / get_recent_accident_logs: PASS")

    # Test photo operations
    log_photo_upload("tok123", {
        "filename": "test.jpg",
        "originalName": "photo.jpg",
        "size": 1024,
        "patientName": "Ravi",
        "timestamp": "2024-01-01",
        "uploadedAt": "2024-01-01T00:00:00Z",
        "viewToken": "view_abc123",
    })
    photo = get_photo_by_view_token("view_abc123")
    assert photo is not None, "Photo not found by view token"
    assert photo["viewed"] is False, "New photo should not be viewed"
    assert photo["token"] == "tok123", "Photo should have user token"
    assert "createdAt" in photo, "Photo should have createdAt"
    print("  log_photo_upload / get_photo_by_view_token: PASS")

    mark_photo_as_viewed("view_abc123")
    photo2 = get_photo_by_view_token("view_abc123")
    assert photo2["viewed"] is True, "Photo should be marked as viewed"
    assert "viewedAt" in photo2, "Photo should have viewedAt after viewing"
    print("  mark_photo_as_viewed: PASS")


def test_token_service():
    """Test 3: Token encode/decode roundtrip."""
    print("--- Test 3: Token Service ---")
    from app.services.token_service import encode_user_token, decode_user_token

    user = {
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

    token = encode_user_token(user)
    assert isinstance(token, str), "Token should be string"
    assert "=" not in token, "Token should not have = padding (base64url)"
    assert " " not in token, "Token should not have spaces"
    print(f"  Token generated ({len(token)} chars): {token[:50]}...")

    decoded = decode_user_token(token)
    assert decoded is not None, "Decode returned None"
    assert decoded["fullName"] == "Ravi Kumar"
    assert decoded["bloodGroup"] == "B+"
    assert len(decoded["emergencyContacts"]) == 2
    assert decoded["emergencyContacts"][0]["name"] == "Sunita"
    assert decoded["emergencyContacts"][0]["phone"] == "9876543210"
    assert decoded["emergencyContacts"][1]["name"] == "Amit"
    assert len(decoded["governmentHelplines"]) == 2
    assert decoded["governmentHelplines"][0]["name"] == "Police"
    assert decoded["governmentHelplines"][0]["number"] == "100"
    assert "createdAt" in decoded
    print("  Encode/decode roundtrip: PASS")

    # Test invalid token
    assert decode_user_token("!!!invalid!!!") is None
    assert decode_user_token("") is None
    print("  Invalid token handling: PASS")


def test_qr_service():
    """Test 4: QR code generation."""
    print("--- Test 4: QR Service ---")
    from app.services.qr_service import generate_qr_png

    png_bytes = generate_qr_png("https://example.com/scan/test123")
    assert isinstance(png_bytes, bytes), "Should return bytes"
    assert len(png_bytes) > 100, f"PNG too small: {len(png_bytes)} bytes"
    assert png_bytes[:8] == b"\x89PNG\r\n\x1a\n", "Should be valid PNG header"
    print(f"  Generated QR PNG: {len(png_bytes)} bytes")

    # Test custom size
    png_small = generate_qr_png("https://example.com", size=256)
    assert isinstance(png_small, bytes)
    print(f"  Generated 256px QR: {len(png_small)} bytes")
    print("  QR generation: PASS")


def test_validation():
    """Test 5: Phone validation and cleaning."""
    print("--- Test 5: Validation ---")
    from app.services.validation import is_valid_indian_phone, clean_phone_number

    # is_valid_indian_phone — accepts any non-empty string
    assert is_valid_indian_phone("9876543210") is True
    assert is_valid_indian_phone("100") is True
    assert is_valid_indian_phone("+91-98765-43210") is True
    assert is_valid_indian_phone("") is False
    assert is_valid_indian_phone("   ") is False
    print("  is_valid_indian_phone: PASS")

    # clean_phone_number — strips non-digits
    assert clean_phone_number("9876543210") == "9876543210"
    assert clean_phone_number("+91-98765-43210") == "919876543210"
    assert clean_phone_number("(022) 2345-6789") == "02223456789"
    assert clean_phone_number("abc") == ""
    print("  clean_phone_number: PASS")


def test_helpers():
    """Test 6: Utility helpers."""
    print("--- Test 6: Helpers ---")
    from app.utils.helpers import generate_token, encode_base64

    # generate_token — 32-char hex
    tok1 = generate_token()
    tok2 = generate_token()
    assert len(tok1) == 32, f"Token length should be 32, got {len(tok1)}"
    assert tok1 != tok2, "Tokens should be unique"
    assert all(c in "0123456789abcdef" for c in tok1), "Should be hex only"
    print(f"  generate_token: {tok1}")
    print("  generate_token: PASS")

    # encode_base64
    assert encode_base64("9876543210") == "OTg3NjU0MzIxMA=="
    assert encode_base64("hello") == "aGVsbG8="
    assert encode_base64("") == ""
    print("  encode_base64: PASS")


def test_circular_imports():
    """Test 7: Circular import check."""
    print("--- Test 7: Circular Import Check ---")
    # Import everything at once to detect circular deps
    from app.config import settings
    from app.database import save_user, get_user, get_stats
    from app.services.token_service import encode_user_token, decode_user_token
    from app.services.qr_service import generate_qr_png
    from app.services.validation import is_valid_indian_phone, clean_phone_number
    from app.utils.helpers import generate_token, encode_base64
    print("  No circular imports detected: PASS")


if __name__ == "__main__":
    passed = 0
    failed = 0
    errors = []

    tests = [
        test_config,
        test_database,
        test_token_service,
        test_qr_service,
        test_validation,
        test_helpers,
        test_circular_imports,
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
    print(f"  Module 1 Verification: {passed}/{passed + failed} tests passed")
    if errors:
        print(f"  FAILURES:")
        for name, err in errors:
            print(f"    {name}: {err}")
        sys.exit(1)
    else:
        print("  ALL TESTS PASSED!")
    print("=" * 50)
