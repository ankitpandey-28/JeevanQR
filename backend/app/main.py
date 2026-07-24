import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

try:
    from app.config import settings
    from app.middleware.error_handler import http_exception_handler, generic_exception_handler
    from app.routers import registration, qr, users, photos, stats, pages
except ModuleNotFoundError:
    from backend.app.config import settings
    from backend.app.middleware.error_handler import http_exception_handler, generic_exception_handler
    from backend.app.routers import registration, qr, users, photos, stats, pages

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """FastAPI lifespan handler (replaces deprecated on_event)."""
    logger.info('=========================================')
    logger.info('  QR Emergency Alert System (FastAPI)')
    logger.info('=========================================')
    logger.info(f'  Environment: {settings.ENVIRONMENT}')
    logger.info(f'  Serverless: {settings.is_serverless}')
    logger.info('=========================================')
    yield


app = FastAPI(
    title='QR Emergency Alert System',
    description='Backend API for JeevanQR emergency QR code system',
    version='1.0.0',
    lifespan=lifespan,
)

# CORS middleware
if settings.ALLOWED_ORIGIN:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.ALLOWED_ORIGIN],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

# Exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, generic_exception_handler)

# Include routers - ORDER MATTERS!
# API routes must come BEFORE static file mounts
app.include_router(registration.router)
app.include_router(qr.router)
app.include_router(users.router)
app.include_router(photos.router)
app.include_router(stats.router)
app.include_router(pages.router)

# Static file mounts - AFTER routers
# Mount /css, /js from frontend directory
app.mount('/css', StaticFiles(directory=str(settings.FRONTEND_DIR / 'css')), name='css')
app.mount('/js', StaticFiles(directory=str(settings.FRONTEND_DIR / 'js')), name='js')

# Mount uploads directory
if settings.UPLOADS_DIR.exists() or not settings.is_serverless:
    settings.UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    app.mount('/uploads', StaticFiles(directory=str(settings.UPLOADS_DIR)), name='uploads')

# Serve favicon and other static files from frontend root
# This must be LAST (catch-all)
app.mount('/', StaticFiles(directory=str(settings.FRONTEND_DIR), html=False), name='frontend_static')
