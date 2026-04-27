from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

logger = logging.getLogger(__name__)

class AppException(Exception):
    pass


class ShipmentNotFoundError(AppException):
    pass


class InvalidStatusTransitionError(AppException):
    pass

class TenantNotFoundError(Exception):
    pass


class UserAlreadyExistsError(Exception):
    pass


class InvalidCredentialsError(Exception):
    pass


async def http_exception_handler(request: Request, error: HTTPException):
    return JSONResponse(
        status_code=error.status_code,
        content={
            "success": False,
            "error": error.detail
        }
    )
async def validation_exception_handler(request: Request, error: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": "Validation failed",
            "details": error.errors()
        }
    )

async def generic_exception_handler(request: Request, error: Exception):
    logger.exception("Unhandled server error")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error"
        }
    )
