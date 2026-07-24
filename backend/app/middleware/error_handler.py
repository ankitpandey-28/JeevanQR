"""
QR Emergency Alert System - Global Error Handlers
Converted from: error handling middleware in server.js lines 508-517

Express error handlers:
  // 404 handler
  app.use((req, res) => {
    res.status(404).send('Page not found');
  });

  // Error handler
  app.use((err, req, res, next) => {
    console.error('Server error:', err);
    res.status(500).send('Internal server error');
  });

FastAPI equivalent uses exception handlers registered on the app instance.
These are added in main.py via app.add_exception_handler().
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

    Matches the original Node.js 404 handler:
      res.status(404).send('Page not found')

    For other HTTP errors, returns the exception detail as plain text.

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

    Matches the original Node.js error handler:
      console.error('Server error:', err);
      res.status(500).send('Internal server error');

    Args:
        request: The incoming request.
        exc: The unhandled exception.

    Returns:
        PlainTextResponse with 500 status code.
    """
    logger.error("Server error: %s", exc, exc_info=True)
    return PlainTextResponse("Internal server error", status_code=500)
