"""
QR Emergency Alert System - Database Module
Converted from: backend/database.js

Simple JSON file-based storage for users, accident logs, and photos.
Uses in-memory storage with optional JSON file persistence.
In serverless environments (Vercel), file I/O is skipped and data
lives only in memory for the duration of the function invocation.
"""

import json
import logging
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from backend.app.config import settings

logger = logging.getLogger(__name__)

# ============================================
# IN-MEMORY STORAGE
# ============================================

users: Dict[str, dict] = {}          # token -> user object
accident_logs: List[dict] = []       # Array of accident location logs
photos: Dict[str, dict] = {}         # viewToken -> photo info

# ============================================
# FILE PATHS
# ============================================

USERS_FILE = settings.DATABASE_DIR / "users.json"
ACCIDENT_LOGS_FILE = settings.DATABASE_DIR / "accident_logs.json"
PHOTOS_FILE = settings.DATABASE_DIR / "photos.json"


# ============================================
# INITIALIZATION
# ============================================

def ensure_database_dir() -> None:
    """Ensure database directory exists.
    Skip directory creation in serverless environments.

    Original: ensureDatabaseDir() in database.js lines 34-45
    """
    if settings.is_serverless:
        logger.info("[DB] Running in serverless environment - using in-memory storage")
        return
    settings.DATABASE_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("[DB] Database directory ready: %s", settings.DATABASE_DIR)


# ============================================
# LOAD FUNCTIONS
# ============================================

def load_users() -> None:
    """Load users from users.json file.
    Skip if running in serverless environment.

    Original: loadUsers() in database.js lines 50-70
    """
    global users
    if settings.is_serverless:
        logger.info("[DB] Running in serverless environment - using in-memory users")
        return
    try:
        if USERS_FILE.exists():
            raw = USERS_FILE.read_text(encoding="utf-8")
            parsed = json.loads(raw or "{}")
            if isinstance(parsed, dict):
                users = parsed
                logger.info("[DB] Loaded %d users from database", len(users))
    except (json.JSONDecodeError, OSError) as err:
        logger.error("[DB] Failed to load users.json: %s", err)
        users = {}


def load_accident_logs() -> None:
    """Load accident logs from accident_logs.json file.
    Skip if running in serverless environment.

    Original: loadAccidentLogs() in database.js lines 75-95
    """
    global accident_logs
    if settings.is_serverless:
        logger.info("[DB] Running in serverless environment - using in-memory accident logs")
        return
    try:
        if ACCIDENT_LOGS_FILE.exists():
            raw = ACCIDENT_LOGS_FILE.read_text(encoding="utf-8")
            parsed = json.loads(raw or "[]")
            if isinstance(parsed, list):
                accident_logs = parsed
                logger.info("[DB] Loaded %d accident logs", len(accident_logs))
    except (json.JSONDecodeError, OSError) as err:
        logger.error("[DB] Failed to load accident_logs.json: %s", err)
        accident_logs = []


def load_photos() -> None:
    """Load photos from photos.json file.
    Skip if running in serverless environment.

    Original: loadPhotos() in database.js lines 100-120
    """
    global photos
    if settings.is_serverless:
        logger.info("[DB] Running in serverless environment - using in-memory photos")
        return
    try:
        if PHOTOS_FILE.exists():
            raw = PHOTOS_FILE.read_text(encoding="utf-8")
            parsed = json.loads(raw or "{}")
            if isinstance(parsed, dict):
                photos = parsed
                logger.info("[DB] Loaded %d photos from database", len(photos))
    except (json.JSONDecodeError, OSError) as err:
        logger.error("[DB] Failed to load photos.json: %s", err)
        photos = {}


# ============================================
# SAVE FUNCTIONS
# ============================================

def save_users() -> None:
    """Save users to users.json file.
    Skip in serverless environments.

    Original: saveUsers() in database.js lines 125-137
    """
    if settings.is_serverless:
        logger.info("[DB] Running in serverless environment - users stored in memory only")
        return
    try:
        USERS_FILE.write_text(json.dumps(users, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as err:
        logger.error("[DB] Failed to save users.json: %s", err)


def save_accident_logs() -> None:
    """Save accident logs to accident_logs.json file.
    Skip in serverless environments.

    Original: saveAccidentLogs() in database.js lines 142-154
    """
    if settings.is_serverless:
        logger.info("[DB] Running in serverless environment - accident logs stored in memory only")
        return
    try:
        ACCIDENT_LOGS_FILE.write_text(json.dumps(accident_logs, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as err:
        logger.error("[DB] Failed to save accident_logs.json: %s", err)


def save_photos() -> None:
    """Save photos to photos.json file.
    Skip in serverless environments.

    Original: savePhotos() in database.js lines 159-171
    """
    if settings.is_serverless:
        logger.info("[DB] Running in serverless environment - photos stored in memory only")
        return
    try:
        PHOTOS_FILE.write_text(json.dumps(photos, indent=2, ensure_ascii=False), encoding="utf-8")
    except OSError as err:
        logger.error("[DB] Failed to save photos.json: %s", err)


# ============================================
# USER OPERATIONS
# ============================================

def save_user(token: str, user: dict) -> None:
    """Save a new user.

    Original: saveUser() in database.js lines 182-186

    Args:
        token: Unique token identifying the user.
        user: User data dictionary.
    """
    users[token] = user
    save_users()
    logger.info("[DB] Saved user: %s (Token: %s...)", user.get("fullName", ""), token[:8])


def get_user(token: str) -> Optional[dict]:
    """Get user by token.

    Original: getUser() in database.js lines 193-195

    Args:
        token: User token.

    Returns:
        User data dict or None if not found.
    """
    return users.get(token)


def get_all_users() -> dict:
    """Get all users (for admin).

    Original: getAllUsers() in database.js lines 201-203

    Returns:
        Dict of all users keyed by token.
    """
    return users


def delete_user(token: str) -> bool:
    """Delete user by token.

    Original: deleteUser() in database.js lines 210-217

    Args:
        token: User token.

    Returns:
        True if user was deleted, False if not found.
    """
    if token in users:
        del users[token]
        save_users()
        return True
    return False


# ============================================
# ACCIDENT LOG OPERATIONS
# ============================================

def log_accident_location(token: str, location_data: dict) -> None:
    """Log an accident location.

    Original: logAccidentLocation() in database.js lines 228-240
    The original creates a flat object: { id: Date.now(), token, ...locationData }

    Args:
        token: User token.
        location_data: Location information dict with userName, latitude, longitude, mapsUrl, reportedAt.
    """
    log_entry = {
        "id": int(time.time() * 1000),
        "token": token,
        **location_data,
    }
    accident_logs.append(log_entry)
    save_accident_logs()
    logger.info("[DB] Accident location logged for: %s", location_data.get("userName", ""))
    logger.info("     Location: %s", location_data.get("mapsUrl", ""))


def get_recent_accident_logs(limit: int = 10) -> list:
    """Get recent accident logs.

    Original: getRecentAccidentLogs() in database.js lines 247-249

    Args:
        limit: Maximum number of logs to return.

    Returns:
        List of recent accident logs (most recent first).
    """
    return list(reversed(accident_logs[-limit:]))


# ============================================
# PHOTO OPERATIONS
# ============================================

def log_photo_upload(token: str, photo_info: dict) -> None:
    """Log photo upload.

    Original: logPhotoUpload() in database.js lines 277-287

    Args:
        token: User token.
        photo_info: Photo information dict with filename, originalName, size,
                    patientName, timestamp, uploadedAt, viewToken.
    """
    view_token = photo_info.get("viewToken")
    if not view_token:
        return
    photos[view_token] = {
        **photo_info,
        "token": token,
        "viewed": False,
        "createdAt": datetime.now(timezone.utc).isoformat(),
    }
    save_photos()
    logger.info("[DB] Photo uploaded: %s (ViewToken: %s...)", photo_info.get("filename", ""), view_token[:8])


def get_photo_by_view_token(view_token: str) -> Optional[dict]:
    """Get photo by view token.

    Original: getPhotoByViewToken() in database.js lines 294-296

    Args:
        view_token: Photo view token.

    Returns:
        Photo info dict or None if not found.
    """
    return photos.get(view_token)


def mark_photo_as_viewed(view_token: str) -> None:
    """Mark photo as viewed (one-time access).

    Original: markPhotoAsViewed() in database.js lines 302-309

    Args:
        view_token: Photo view token.
    """
    if view_token in photos:
        photos[view_token]["viewed"] = True
        photos[view_token]["viewedAt"] = datetime.now(timezone.utc).isoformat()
        save_photos()
        logger.info("[DB] Photo marked as viewed: %s...", view_token[:8])


# ============================================
# STATISTICS
# ============================================

def get_stats() -> dict:
    """Get database statistics.

    Original: getStats() in database.js lines 259-266
    Returns keys: totalUsers, totalAccidentLogs, totalPhotos, lastUpdated

    Returns:
        Stats dictionary matching the original Node.js response format.
    """
    return {
        "totalUsers": len(users),
        "totalAccidentLogs": len(accident_logs),
        "totalPhotos": len(photos),
        "lastUpdated": datetime.now(timezone.utc).isoformat(),
    }


# ============================================
# INITIALIZE ON MODULE LOAD
# ============================================

ensure_database_dir()
load_users()
load_accident_logs()
load_photos()
