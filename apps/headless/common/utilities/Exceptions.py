import re
import structlog

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import exception_handler
from ..constants import ERR_CODES

logger = structlog.get_logger(__name__)


def extract_integrity_error_context(msg):
    """
        Helper to handle integrity errors gracefully.
        Checks the error string for error identification using
        regex and string matching and returns appropriate error message.
    """
    user_msg = "Data Integrity Error"

    # Detect UNIQUE constraint violations
    if "UNIQUE constraint failed" in msg:
        try:
            field = msg.split(":")[-1].strip()
            user_msg = f"{field} already exists."
        except Exception:
            user_msg = "Record already exists."
    # Handle duplicate key from Postgres (different message pattern)
    elif "duplicate entry" in msg.lower():
        match = re.search(r"Key \(([^)]+)\)=", msg)
        if match:
            field = match.group(1)
            field = field.replace('_', ' ').capitalize()
            user_msg = f"{field} already exists."
        else:
            user_msg = "Record already exists."
    # Handle foreign key constraint failure
    elif "FOREIGN KEY constraint failed" in msg or "violates foreign key constraint" in msg:
        user_msg = "Invalid reference — related record not found."

    return user_msg


def flatten_serializer_errors(detail, parent_field="") -> str:
    """
    Recursively flattens DRF serializer error details into a readable string.
    Handles nested dicts, lists, and tuples gracefully.
    Example output:
      "email: This field is required; profile.address.city: Invalid value"
    """
    messages = []

    if isinstance(detail, (list, tuple)):
        for error in detail:
            # Nested dict or list inside a list
            if isinstance(error, (dict, list, tuple)):
                messages.append(flatten_serializer_errors(error, parent_field))
            else:
                field_label = f"{parent_field}: " if (parent_field and parent_field != 'non_field_errors') else ""
                messages.append(f"{field_label}{error}")
        return " | ".join(messages)

    elif isinstance(detail, dict):
        for field, errors in detail.items():
            field_path = f"{parent_field}.{field}" if parent_field else field
            messages.append(flatten_serializer_errors(errors, field_path))
        return " | ".join(messages)

    # Handle unexpected types (like strings, ErrorDetail, etc.)
    else:
        return f"{parent_field}: {detail}" if (parent_field and parent_field != 'non_field_errors') else str(detail)



def headless_exception_handler(exc, context):
    """
    Clean, consistent output for ALL headless errors.
    """
    response = exception_handler(exc, context)

    
    # Integrity errors (duplicate key, FK violation, etc)
    if isinstance(exc, IntegrityError):
        logger.exception("IntegrityError", data={"exc": exc})
        msg = extract_integrity_error_context(str(exc))
        return Response({
            "status": False,
            "results": False,
            "message": msg or "Database integrity error",
            "data": None,
            "error_code": ERR_CODES.INTEGRITY_ERR,
        }, status=status.HTTP_400_BAD_REQUEST)

    # Not found raised manually by your domain layer
    elif isinstance(exc, ObjectDoesNotExist):
        logger.exception("HEADLESS_ERROR", data={"exc_info": exc})    
        return Response({
            "status": False,
            "results": False,
            "message": "Resource not found !",
            "data": None,
            "error_code": ERR_CODES.RESOURCE_NOT_FOUND,
        }, status=404)
    
    # Serializer Validation Errors
    elif isinstance(exc, ValidationError):
        msg = flatten_serializer_errors(exc.detail)
        return Response({
            "status": False,
            "results": False,
            "message": msg or "Validation Failed",
            "data": None,
            "error_code": ERR_CODES.VALIDATION_ERR,
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Auth Permission Exception
    elif isinstance(exc, PermissionDenied):
        res = {
            "status": False,
            "results": False,
            "message": "Permission Denied",
            "data": None,
            "error_code": ERR_CODES.API_KEY_ERR,
        }
        res = response.data or res
        return Response(res, response.status_code)
    
    # Any Known Response Category
    elif response is not None:
        detail = response.data.get("detail", None)
        return Response({
            "status": False,
            "results": False,
            "message": detail or "Error",
            "data": None,
            "error_code": getattr(exc, "error_code", None),
        }, status=response.status_code)
    
    logger.exception("HEADLESS_ERROR", data={"exc_info": exc})    

    return Response({
        "status": False,
        "results": False,
        "message": "Internal server error",
        "data": None,
        "error_code": ERR_CODES.INTERNAL_ERR,
    }, status=500)


class HeadlessException(APIException):
    status_code = 500
    default_detail = "Internal server error"
    default_code = ERR_CODES.INTERNAL_ERR