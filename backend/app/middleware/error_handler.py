"""
QR Emergency Alert System - Global Error Handlers

Exception handlers registered on the FastAPI app instance via
app.add_exception_handler() in main.py.
"""

import logging

from fastapi import Request
from fastapi.responses import PlainTextResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> PlainTextResponse:
    """Handle HTTP exceptions (404, etc.).

    Returns 'Page not found' for 404 errors. For other HTTP errors,
    returns the exception detail as plain text.

    Args:
        request: The incoming request.
        exc: The HTTP exception raised.

    Returns:
        PlainTextResponse with appropriate status code.
    """
    if exc.status_code == 404:
        return PlainTextResponse("Page not found", status_code=404)
    return PlainTextResponse(str(exc.detail), status_code=exc.status_code)


async def generic_exception_handler(
    request: Request, exc: Exception
) -> PlainTextResponse:
    """Handle unhandled exceptions (500 Internal Server Error).

    Args:
        request: The incoming request.
        exc: The unhandled exception.

    Returns:
        PlainTextResponse with 500 status code.
    """
    logger.exception("Server error: %s", exc)
    return PlainTextResponse("Internal server error", status_code=500)
