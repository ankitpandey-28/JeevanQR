"""API endpoint pytest suite."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import users, accident_logs, photos
from app.utils.helpers import encode_base64
from app.services.token_service import decode_user_token


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage before each test."""
    users.clear()
    accident_logs.clear()
    photos.clear()
    yield


client = TestClient(app)


class TestRegistrationAPI:
    """POST /api/register - Full API contract verification."""

    def test_response_format(self):
        """Response must contain exactly: token, publicUrl, qrImageUrl."""
        resp = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"token", "publicUrl", "qrImageUrl"}
        assert isinstance(data["token"], str)
        assert data["publicUrl"] == f"/scan/{data['token']}"
        assert data["qrImageUrl"] == f"/api/qr/{data['token']}"

    def test_token_is_self_contained(self):
        """Token can be decoded without database lookup (serverless compatible)."""
        resp = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = resp.json()["token"]
        decoded = decode_user_token(token)
        assert decoded is not None
        assert decoded["fullName"] == "Ravi Kumar"
        assert decoded["bloodGroup"] == "B+"

    def test_error_response_format(self):
        """Error responses have { error: string } format."""
        resp = client.post("/api/register", json={
            "fullName": "",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data
        assert isinstance(data["error"], str)

    def test_hindi_error_messages_preserved(self):
        """Hindi error messages are preserved."""
        resp = client.post("/api/register", json={
            "fullName": "Test",
            "bloodGroup": "B+",
            "emergencyContacts": [],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        assert "आपातकालीन" in resp.json()["error"]


class TestPublicUserAPI:
    """GET /api/users/{token}/public - Full API contract verification."""

    def test_response_format(self):
        """Response must contain: fullName, bloodGroup, emergencyContacts (with phoneEncoded), governmentHelplines."""
        reg = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = reg.json()["token"]

        resp = client.get(f"/api/users/{token}/public")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"fullName", "bloodGroup", "emergencyContacts", "governmentHelplines"}
        assert data["fullName"] == "Ravi Kumar"
        assert data["bloodGroup"] == "B+"

        # Emergency contacts use phoneEncoded (not raw phone)
        ec = data["emergencyContacts"][0]
        assert set(ec.keys()) == {"name", "phoneEncoded"}
        assert ec["name"] == "Sunita"
        assert ec["phoneEncoded"] == encode_base64("9876543210")

        # Government helplines use 'number' field
        gh = data["governmentHelplines"][0]
        assert set(gh.keys()) == {"name", "number"}
        assert gh["name"] == "Police"
        assert gh["number"] == "100"

    def test_error_response_format(self):
        """404 returns { error: 'User not found' }."""
        resp = client.get("/api/users/invalid_token/public")
        assert resp.status_code == 404
        assert resp.json() == {"error": "User not found"}


class TestLocationAPI:
    """POST /api/users/{token}/location - Full API contract verification."""

    def test_response_format(self):
        """Response must be { ok: true }."""
        reg = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = reg.json()["token"]

        resp = client.post(f"/api/users/{token}/location", json={
            "latitude": 28.6139,
            "longitude": 77.2090,
            "mapsUrl": "https://maps.google.com/?q=28.6139,77.2090",
        })
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

    def test_flat_log_structure(self):
        """Log entry has flat structure: { id, token, userName, latitude, longitude, mapsUrl, reportedAt }."""
        reg = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = reg.json()["token"]

        client.post(f"/api/users/{token}/location", json={
            "latitude": 28.6139,
            "longitude": 77.2090,
            "mapsUrl": "https://maps.google.com/?q=28.6139,77.2090",
        })

        log = accident_logs[0]
        assert "id" in log
        assert "token" in log
        assert "userName" in log
        assert "latitude" in log
        assert "longitude" in log
        assert "mapsUrl" in log
        assert "reportedAt" in log
        assert log["token"] == token
        assert log["userName"] == "Ravi Kumar"


class TestStatsAPI:
    """GET /api/stats - Full API contract verification."""

    def test_response_format(self):
        """Response must contain: totalUsers, totalAccidentLogs, totalPhotos, lastUpdated."""
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"totalUsers", "totalAccidentLogs", "totalPhotos", "lastUpdated"}
        assert isinstance(data["totalUsers"], int)
        assert isinstance(data["totalAccidentLogs"], int)
        assert isinstance(data["totalPhotos"], int)
        assert isinstance(data["lastUpdated"], str)


class TestQRAPI:
    """GET /api/qr/{token} - Full API contract verification."""

    def test_response_headers(self):
        """Response has Content-Type: image/png and Cache-Control header."""
        reg = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = reg.json()["token"]

        resp = client.get(f"/api/qr/{token}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        assert "max-age=31536000" in resp.headers.get("cache-control", "")

    def test_invalid_token_returns_404_with_message(self):
        """Invalid token returns 404 with 'Unknown QR code'."""
        resp = client.get("/api/qr/invalid_token")
        assert resp.status_code == 404
        assert resp.text == "Unknown QR code"


class TestPhotoUploadAPI:
    """POST /api/upload-photo - Full API contract verification."""

    def test_response_format(self):
        """Response must contain: success, photoUrl, secureUrl, viewToken, message."""
        reg = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = reg.json()["token"]

        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        resp = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": token},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert set(data.keys()) == {"success", "photoUrl", "secureUrl", "viewToken", "message"}
        assert data["success"] is True
        assert data["photoUrl"].startswith("/uploads/")
        assert data["secureUrl"].startswith("http")
        assert data["viewToken"] is not None
        assert data["message"] == "Photo uploaded successfully"

    def test_photo_stored_in_database(self):
        """Photo metadata is stored in database with viewed=False."""
        reg = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = reg.json()["token"]

        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        resp = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": token, "patientName": "Ravi"},
        )
        view_token = resp.json()["viewToken"]

        assert view_token in photos
        assert photos[view_token]["token"] == token
        assert photos[view_token]["viewed"] is False
        assert photos[view_token]["patientName"] == "Ravi"


class TestPhotoViewAPI:
    """GET /photo/{viewToken} - Full API contract verification."""

    def test_one_time_access(self):
        """Photo can only be viewed once (second view returns 410)."""
        reg = client.post("/api/register", json={
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        })
        token = reg.json()["token"]

        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        upload_resp = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": token},
        )
        view_token = upload_resp.json()["viewToken"]

        # First view - should succeed
        first = client.get(f"/photo/{view_token}")
        assert first.status_code == 200

        # Second view - should be 410 Gone
        second = client.get(f"/photo/{view_token}")
        assert second.status_code == 410
        assert "expired" in second.text

    def test_not_found_returns_404(self):
        """Non-existent view token returns 404."""
        resp = client.get("/photo/nonexistent")
        assert resp.status_code == 404
        assert "expired" in resp.text


class TestErrorHandlingAPI:
    """Error handlers - Full API contract verification."""

    def test_404_returns_page_not_found(self):
        """Unknown route returns 'Page not found' with 404."""
        resp = client.get("/this-route-does-not-exist")
        assert resp.status_code == 404
        assert resp.text == "Page not found"

    def test_404_for_api_unknown_route(self):
        """Unknown API route returns 404."""
        resp = client.get("/api/unknown-route")
        assert resp.status_code == 404
        assert resp.text == "Page not found"


class TestEndToEndFlow:
    """Complete end-to-end flow matching real user journey."""

    def test_full_user_journey(self):
        """Complete flow: register -> get QR -> get public info -> log location -> upload photo -> view photo."""
        # 1. Register
        reg = client.post("/api/register", json={
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
        })
        assert reg.status_code == 200
        token = reg.json()["token"]

        # 2. Get QR code
        qr = client.get(f"/api/qr/{token}")
        assert qr.status_code == 200
        assert qr.headers["content-type"] == "image/png"

        # 3. Get public info
        pub = client.get(f"/api/users/{token}/public")
        assert pub.status_code == 200
        assert pub.json()["fullName"] == "Ravi Kumar"
        assert pub.json()["emergencyContacts"][0]["phoneEncoded"] == encode_base64("9876543210")

        # 4. Log location
        loc = client.post(f"/api/users/{token}/location", json={
            "latitude": 28.6139,
            "longitude": 77.2090,
            "mapsUrl": "https://maps.google.com/?q=28.6139,77.2090",
        })
        assert loc.status_code == 200
        assert loc.json() == {"ok": True}

        # 5. Upload photo
        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        upload = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": token, "patientName": "Ravi"},
        )
        assert upload.status_code == 200
        view_token = upload.json()["viewToken"]

        # 6. View photo (first time)
        view = client.get(f"/photo/{view_token}")
        assert view.status_code == 200

        # 7. View photo (second time - should be expired)
        expired = client.get(f"/photo/{view_token}")
        assert expired.status_code == 410

        # 8. Check stats
        stats = client.get("/api/stats")
        assert stats.status_code == 200
        assert stats.json()["totalUsers"] == 1
        assert stats.json()["totalAccidentLogs"] == 1
        assert stats.json()["totalPhotos"] == 1