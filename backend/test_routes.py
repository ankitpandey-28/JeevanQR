

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import users, accident_logs, photos


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage before each test."""
    users.clear()
    accident_logs.clear()
    photos.clear()
    yield


client = TestClient(app)


class TestRegistrationRoute:
    """Test POST /api/register."""

    VALID_PAYLOAD = {
        "fullName": "Ravi Kumar",
        "bloodGroup": "B+",
        "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
        "governmentHelplines": [{"name": "Police", "number": "100"}],
    }

    def test_successful_registration(self):
        """Returns token, publicUrl, qrImageUrl."""
        resp = client.post("/api/register", json=self.VALID_PAYLOAD)
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert "publicUrl" in data
        assert "qrImageUrl" in data
        assert data["publicUrl"].startswith("/scan/")
        assert data["qrImageUrl"].startswith("/api/qr/")

        # Verify user saved in database
        token = data["token"]
        assert token in users
        assert users[token]["fullName"] == "Ravi Kumar"

    def test_missing_full_name_returns_400(self):
        """Missing fullName or bloodGroup returns 400 with Hindi/English error."""
        payload = self.VALID_PAYLOAD.copy()
        del payload["fullName"]
        resp = client.post("/api/register", json=payload)
        assert resp.status_code == 400
        assert "Missing required fields" in resp.json()["error"]

    def test_missing_blood_group_returns_400(self):
        """Missing bloodGroup returns 400."""
        payload = self.VALID_PAYLOAD.copy()
        del payload["bloodGroup"]
        resp = client.post("/api/register", json=payload)
        assert resp.status_code == 400

    def test_empty_emergency_contacts_returns_400(self):
        """Empty emergency contacts returns 400."""
        payload = self.VALID_PAYLOAD.copy()
        payload["emergencyContacts"] = []
        resp = client.post("/api/register", json=payload)
        assert resp.status_code == 400
        assert "emergency contact" in resp.json()["error"]

    def test_empty_government_helplines_returns_400(self):
        """Empty government helplines returns 400."""
        payload = self.VALID_PAYLOAD.copy()
        payload["governmentHelplines"] = []
        resp = client.post("/api/register", json=payload)
        assert resp.status_code == 400
        assert "helpline" in resp.json()["error"]

    def test_invalid_contact_phone_returns_400(self):
        """Invalid emergency contact phone returns 400."""
        payload = self.VALID_PAYLOAD.copy()
        payload["emergencyContacts"] = [{"name": "Test", "phone": ""}]
        resp = client.post("/api/register", json=payload)
        assert resp.status_code == 400

    def test_invalid_helpline_number_returns_400(self):
        """Invalid helpline number returns 400."""
        payload = self.VALID_PAYLOAD.copy()
        payload["governmentHelplines"] = [{"name": "Test", "number": ""}]
        resp = client.post("/api/register", json=payload)
        assert resp.status_code == 400

    def test_blood_group_normalized_to_uppercase(self):
        """bloodGroup is trimmed and uppercased."""
        payload = self.VALID_PAYLOAD.copy()
        payload["bloodGroup"] = "  b+  "
        resp = client.post("/api/register", json=payload)
        token = resp.json()["token"]
        assert users[token]["bloodGroup"] == "B+"

    def test_phone_cleaned_to_digits(self):
        """Phone numbers are cleaned to digits only."""
        payload = self.VALID_PAYLOAD.copy()
        payload["emergencyContacts"] = [{"name": "Test", "phone": "+91-98765-43210"}]
        resp = client.post("/api/register", json=payload)
        token = resp.json()["token"]
        assert users[token]["emergencyContacts"][0]["phone"] == "919876543210"


class TestQRRoute:
    """Test GET /api/qr/{token}."""

    def test_qr_generation_for_valid_token(self):
        """Returns PNG image with proper content type and caching."""
        # Register a user first
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        reg_resp = client.post("/api/register", json=payload)
        token = reg_resp.json()["token"]

        # Get QR code
        resp = client.get(f"/api/qr/{token}")
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        assert "cache-control" in resp.headers
        assert resp.content[:8] == b"\x89PNG\r\n\x1a\n"  # PNG magic bytes

    def test_qr_for_invalid_token_returns_404(self):
        """Unknown token returns 404 with 'Unknown QR code'."""
        resp = client.get("/api/qr/invalid_token_here")
        assert resp.status_code == 404
        assert resp.text == "Unknown QR code"


class TestPublicUserRoute:
    """Test GET /api/users/{token}/public."""

    def test_public_user_data(self):
        """Returns user data with base64-encoded phone numbers."""
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        reg_resp = client.post("/api/register", json=payload)
        token = reg_resp.json()["token"]

        resp = client.get(f"/api/users/{token}/public")
        assert resp.status_code == 200
        data = resp.json()
        assert data["fullName"] == "Ravi Kumar"
        assert data["bloodGroup"] == "B+"
        assert data["emergencyContacts"][0]["name"] == "Sunita"
        assert "phoneEncoded" in data["emergencyContacts"][0]
        assert "phone" not in data["emergencyContacts"][0]  # Raw phone NOT exposed
        assert data["governmentHelplines"][0]["name"] == "Police"

    def test_public_user_not_found(self):
        """Non-existent token returns 404."""
        resp = client.get("/api/users/invalid_token/public")
        assert resp.status_code == 404
        assert resp.json()["error"] == "User not found"


class TestLocationRoute:
    """Test POST /api/users/{token}/location."""

    def test_log_location(self):
        """Returns { ok: true } and logs the accident location."""
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        reg_resp = client.post("/api/register", json=payload)
        token = reg_resp.json()["token"]

        loc_payload = {
            "latitude": 28.6139,
            "longitude": 77.2090,
            "mapsUrl": "https://maps.google.com/?q=28.6139,77.2090",
        }
        resp = client.post(f"/api/users/{token}/location", json=loc_payload)
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}

        # Verify log stored
        assert len(accident_logs) == 1
        assert accident_logs[0]["token"] == token
        assert accident_logs[0]["latitude"] == 28.6139

    def test_log_location_user_not_found(self):
        """Non-existent token returns 404."""
        resp = client.post("/api/users/invalid_token/location", json={"latitude": 0})
        assert resp.status_code == 404

    def test_log_location_with_empty_body(self):
        """All fields optional - empty body should not error."""
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        reg_resp = client.post("/api/register", json=payload)
        token = reg_resp.json()["token"]

        resp = client.post(f"/api/users/{token}/location", json={})
        assert resp.status_code == 200
        assert resp.json() == {"ok": True}
        assert accident_logs[0]["latitude"] is None


class TestStatsRoute:
    """Test GET /api/stats."""

    def test_stats_response(self):
        """Returns stats with all required keys."""
        resp = client.get("/api/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert "totalUsers" in data
        assert "totalAccidentLogs" in data
        assert "totalPhotos" in data
        assert "lastUpdated" in data

    def test_stats_counts_update(self):
        """Stats reflect actual storage counts."""
        # After registration
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        client.post("/api/register", json=payload)
        stats = client.get("/api/stats").json()
        assert stats["totalUsers"] == 1
        assert stats["totalPhotos"] == 0


class TestPhotoRoute:
    """Test POST /api/upload-photo."""

    def test_photo_upload_success(self):
        """Uploads photo and returns URLs."""
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        reg_resp = client.post("/api/register", json=payload)
        token = reg_resp.json()["token"]

        # Create a test image
        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100  # Minimal PNG

        resp = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": token, "patientName": "Ravi", "timestamp": "2024-01-01"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert "photoUrl" in data
        assert "secureUrl" in data
        assert "viewToken" in data
        assert data["message"] == "Photo uploaded successfully"

        # Verify photo logged in database
        assert data["viewToken"] in photos
        assert photos[data["viewToken"]]["token"] == token

    def test_photo_upload_no_file(self):
        """No photo file returns 400."""
        resp = client.post(
            "/api/upload-photo",
            data={"token": "some_token"},
        )
        assert resp.status_code in (400, 422)  # FastAPI validates File(...) as required

    def test_photo_upload_user_not_found(self):
        """Non-existent token returns 404."""
        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        resp = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": "nonexistent_token"},
        )
        assert resp.status_code == 404
        assert resp.json()["error"] == "User not found"


class TestPhotoViewRoute:
    """Test GET /photo/{viewToken}."""

    def test_photo_view_success(self):
        """Returns photo-view.html for valid, unviewed token."""
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        reg_resp = client.post("/api/register", json=payload)
        token = reg_resp.json()["token"]

        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        upload_resp = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": token},
        )
        view_token = upload_resp.json()["viewToken"]

        resp = client.get(f"/photo/{view_token}", follow_redirects=False)
        assert resp.status_code == 200

    def test_photo_view_expired(self):
        """Already-viewed token returns 410."""
        payload = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        reg_resp = client.post("/api/register", json=payload)
        token = reg_resp.json()["token"]

        test_image = b"\x89PNG\r\n\x1a\n" + b"\x00" * 100
        upload_resp = client.post(
            "/api/upload-photo",
            files={"photo": ("test.png", test_image, "image/png")},
            data={"token": token},
        )
        view_token = upload_resp.json()["viewToken"]

        # First view
        client.get(f"/photo/{view_token}")
        # Second view should be 410
        resp = client.get(f"/photo/{view_token}")
        assert resp.status_code == 410
        assert "expired" in resp.text

    def test_photo_view_not_found(self):
        """Non-existent view token returns 404."""
        resp = client.get("/photo/nonexistent_view_token")
        assert resp.status_code == 404
        assert "expired" in resp.text


class TestPageRoutes:
    """Test static HTML page routes."""

    def test_index_page(self):
        """GET / returns index.html."""
        resp = client.get("/")
        assert resp.status_code == 200

    def test_scan_page(self):
        """GET /scan/{token} returns scan.html."""
        resp = client.get("/scan/test-token-123")
        assert resp.status_code == 200

    def test_qr_page(self):
        """GET /qr.html returns qr.html."""
        resp = client.get("/qr.html")
        assert resp.status_code == 200

    def test_emergency_contacts_page(self):
        """GET /emergency-contacts.html returns the page."""
        resp = client.get("/emergency-contacts.html")
        assert resp.status_code == 200

    def test_government_helplines_page(self):
        """GET /government-helplines.html returns the page."""
        resp = client.get("/government-helplines.html")
        assert resp.status_code == 200

    def test_privacy_settings_page(self):
        """GET /privacy-settings.html returns the page."""
        resp = client.get("/privacy-settings.html")
        assert resp.status_code == 200


class TestErrorHandling:
    """Test error handlers."""

    def test_404_handler(self):
        """Unknown route returns 'Page not found' with 404."""
        resp = client.get("/nonexistent-route")
        assert resp.status_code == 404
        assert resp.text == "Page not found"

    def test_404_for_api_bad_route(self):
        """Unknown API route returns 404."""
        resp = client.get("/api/nonexistent")
        assert resp.status_code == 404
        assert resp.text == "Page not found"