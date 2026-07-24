"""Database pytest suite - tests JSON storage operations match original Node.js behavior."""

import pytest
from app.database import (
    users, accident_logs, photos,
    save_user, get_user, get_all_users, delete_user,
    log_accident_location, get_recent_accident_logs,
    log_photo_upload, get_photo_by_view_token, mark_photo_as_viewed,
    get_stats,
)


@pytest.fixture(autouse=True)
def clear_storage():
    """Clear in-memory storage before each test."""
    users.clear()
    accident_logs.clear()
    photos.clear()
    yield


class TestUserOperations:
    """Test user CRUD operations matching Node.js database.js."""

    def test_save_and_get_user(self):
        """saveUser / getUser roundtrip."""
        user = {
            "fullName": "Ravi Kumar",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "Sunita", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "Police", "number": "100"}],
        }
        save_user("tok1", user)
        retrieved = get_user("tok1")
        assert retrieved is not None
        assert retrieved["fullName"] == "Ravi Kumar"
        assert retrieved["bloodGroup"] == "B+"

    def test_get_user_not_found_returns_none(self):
        """getUser returns None for non-existent token."""
        assert get_user("nonexistent") is None

    def test_get_all_users(self):
        """getAllUsers returns all users dict."""
        save_user("tok1", {"fullName": "User1"})
        save_user("tok2", {"fullName": "User2"})
        all_users = get_all_users()
        assert "tok1" in all_users
        assert "tok2" in all_users
        assert len(all_users) == 2

    def test_delete_user(self):
        """deleteUser removes user and returns True."""
        save_user("tok1", {"fullName": "User1"})
        assert delete_user("tok1") is True
        assert get_user("tok1") is None

    def test_delete_user_not_found(self):
        """deleteUser returns False for non-existent token."""
        assert delete_user("nonexistent") is False

    def test_save_user_with_special_characters(self):
        """User data with Unicode characters (Hindi names)."""
        user = {
            "fullName": "रवि कुमार",
            "bloodGroup": "B+",
            "emergencyContacts": [{"name": "सुनीता", "phone": "9876543210"}],
            "governmentHelplines": [{"name": "पुलिस", "number": "100"}],
        }
        save_user("tok_unicode", user)
        retrieved = get_user("tok_unicode")
        assert retrieved["fullName"] == "रवि कुमार"


class TestAccidentLogOperations:
    """Test accident log operations matching Node.js database.js."""

    def test_log_accident_location(self):
        """logAccidentLocation creates flat log entry with id and token."""
        log_accident_location("tok1", {
            "userName": "Ravi",
            "latitude": 28.6139,
            "longitude": 77.2090,
            "mapsUrl": "https://maps.google.com/?q=28.6139,77.2090",
            "reportedAt": "2024-01-01T00:00:00Z",
        })
        assert len(accident_logs) == 1
        entry = accident_logs[0]
        assert entry["token"] == "tok1"
        assert entry["userName"] == "Ravi"
        assert entry["latitude"] == 28.6139
        assert "id" in entry  # Flat structure (not nested)
        assert isinstance(entry["id"], int)

    def test_get_recent_accident_logs_returns_most_recent_first(self):
        """getRecentAccidentLogs returns most recent logs first (reversed)."""
        log_accident_location("tok1", {"userName": "First", "reportedAt": "2024-01-01T00:00:00Z"})
        log_accident_location("tok2", {"userName": "Second", "reportedAt": "2024-01-02T00:00:00Z"})
        log_accident_location("tok3", {"userName": "Third", "reportedAt": "2024-01-03T00:00:00Z"})

        recent = get_recent_accident_logs(2)
        assert len(recent) == 2
        assert recent[0]["userName"] == "Third"  # Most recent first
        assert recent[1]["userName"] == "Second"

    def test_get_recent_empty_returns_empty_list(self):
        """getRecentAccidentLogs returns empty list when no logs."""
        assert get_recent_accident_logs() == []


class TestPhotoOperations:
    """Test photo operations matching Node.js database.js."""

    def test_log_photo_upload(self):
        """logPhotoUpload stores photo with viewed=False and createdAt."""
        log_photo_upload("tok1", {
            "filename": "emergency-123.jpg",
            "originalName": "photo.jpg",
            "size": 1024,
            "patientName": "Ravi",
            "timestamp": "2024-01-01T00:00:00",
            "uploadedAt": "2024-01-01T00:00:00Z",
            "viewToken": "view_abc",
        })
        assert "view_abc" in photos
        photo = photos["view_abc"]
        assert photo["token"] == "tok1"
        assert photo["viewed"] is False
        assert "createdAt" in photo

    def test_get_photo_by_view_token(self):
        """getPhotoByViewToken returns photo or None."""
        log_photo_upload("tok1", {
            "filename": "test.jpg",
            "originalName": "test.jpg",
            "size": 512,
            "patientName": "Patient",
            "timestamp": "",
            "uploadedAt": "2024-01-01T00:00:00Z",
            "viewToken": "view_xyz",
        })
        photo = get_photo_by_view_token("view_xyz")
        assert photo is not None
        assert photo["filename"] == "test.jpg"

        assert get_photo_by_view_token("nonexistent") is None

    def test_mark_photo_as_viewed(self):
        """markPhotoAsViewed sets viewed=True and adds viewedAt."""
        log_photo_upload("tok1", {
            "filename": "test.jpg",
            "originalName": "test.jpg",
            "size": 512,
            "patientName": "Patient",
            "timestamp": "",
            "uploadedAt": "2024-01-01T00:00:00Z",
            "viewToken": "view_mark",
        })
        mark_photo_as_viewed("view_mark")
        photo = get_photo_by_view_token("view_mark")
        assert photo["viewed"] is True
        assert "viewedAt" in photo

    def test_mark_photo_not_found_does_not_error(self):
        """markPhotoAsViewed on non-existent photo is no-op."""
        mark_photo_as_viewed("nonexistent")  # Should not raise


class TestStatsOperations:
    """Test statistics matching Node.js getStats()."""

    def test_stats_keys_match_nodejs(self):
        """Stats response has exact keys: totalUsers, totalAccidentLogs, totalPhotos, lastUpdated."""
        stats = get_stats()
        assert "totalUsers" in stats
        assert "totalAccidentLogs" in stats
        assert "totalPhotos" in stats
        assert "lastUpdated" in stats
        assert isinstance(stats["totalUsers"], int)
        assert isinstance(stats["totalAccidentLogs"], int)
        assert isinstance(stats["totalPhotos"], int)

    def test_stats_counts(self):
        """Stats counts reflect actual data."""
        save_user("tok1", {"fullName": "User1"})
        log_accident_location("tok1", {"userName": "User1"})
        log_photo_upload("tok1", {
            "filename": "test.jpg",
            "originalName": "test.jpg",
            "size": 512,
            "patientName": "Patient",
            "timestamp": "",
            "uploadedAt": "2024-01-01T00:00:00Z",
            "viewToken": "view_stats",
        })
        stats = get_stats()
        assert stats["totalUsers"] == 1
        assert stats["totalAccidentLogs"] == 1
        assert stats["totalPhotos"] == 1