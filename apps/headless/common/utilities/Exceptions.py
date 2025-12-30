import re
import structlog

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from rest_framework import status
from rest_framework.exceptions import APIException, PermissionDenied, AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.views import exception_handler
from ..constants import ERR_CODES

logger = structlog.get_logger(__name__)


def extract_integrity_error_context(exc):
    """
    A robust and database-agnostic parser for IntegrityError messages.
    Converts raw DB errors into clean human-readable messages.
    Works for Postgres, MySQL, SQLite.
    """
    msg = str(exc)  # always convert to string
    msg_lower = msg.lower()

    # ============================
    # 1. UNIQUE constraint failures
    # ============================

    # SQLite / Django format:
    # UNIQUE constraint failed: table.column
    if "unique constraint failed" in msg_lower:
        parts = msg.split(":")[-1].strip().split(".")
        field = parts[-1] if parts else "Record"
        return f"{field.replace('_', ' ').capitalize()} already exists."

    # PostgreSQL:
    # duplicate key value violates unique constraint "constraint_name"
    # DETAIL: Key (a, b)=(1, 2) already exists.
    if "duplicate key value violates unique constraint" in msg_lower:
        match = re.search(r"Key \(([^)]+)\)=", msg)
        if match:
            fields = match.group(1).replace(" ", "")
            # Support composite keys
            fields = [f.replace("_", " ").capitalize() for f in fields.split(",")]
            if len(fields) == 1:
                return f"{fields[0]} already exists."
            return f"Combination of {', '.join(fields)} already exists."
        return "Record already exists."

    # MySQL:
    # Duplicate entry 'xyz' for key 'table.column'
    if "duplicate entry" in msg_lower:
        match = re.search(r"key '.*\.(.*?)'", msg_lower)
        field = match.group(1) if match else "record"
        field = field.replace("_", " ").capitalize()
        return f"{field} already exists."

    # ============================
    # 2. FOREIGN KEY failures
    # ============================

    # SQLite / Django / MySQL / Postgres:
    if "foreign key constraint failed" in msg_lower or \
       "violates foreign key constraint" in msg_lower:
        return "Invalid reference — related record does not exist."

    # ============================
    # 3. NOT NULL violations
    # ============================

    # PostgreSQL:
    # null value in column "foo" violates not-null constraint
    match = re.search(r'null value in column "([^"]+)"', msg_lower)
    if match:
        field = match.group(1).replace("_", " ").capitalize()
        return f"{field} cannot be null."

    # SQLite:
    # NOT NULL constraint failed: table.column
    if "not null constraint failed" in msg_lower:
        field = msg.split(":")[-1].split(".")[-1].strip()
        field = field.replace("_", " ").capitalize()
        return f"{field} cannot be null."

    # ============================
    # 4. CHECK constraint violations
    # ============================

    if "check constraint" in msg_lower:
        return "Data violates a required condition."

    # ============================
    # 5. Default fallback
    # ============================

    return "Data integrity error."



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
    def default_response(msg="Internal server error", error_code=ERR_CODES.INTERNAL_ERR):
        return {
            "status": False,
            "results": False,
            "message": msg,
            "data": None,
            "error_code": error_code,
        }
    
    # Integrity errors (duplicate key, FK violation, etc)
    if isinstance(exc, IntegrityError):
        logger.exception("IntegrityError", data={"exc": exc})
        msg = extract_integrity_error_context(str(exc))
        msg = msg or "Database integrity error"
        return Response(
            default_response(msg=msg, error_code=ERR_CODES.INTEGRITY_ERR), 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Not found raised manually by your domain layer
    elif isinstance(exc, ObjectDoesNotExist):
        logger.exception("HEADLESS_ERROR", data={"exc_info": exc})    
        return Response(
            default_response(msg="Resource not found !", error_code=ERR_CODES.NOT_FOUND_ERR), 
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Serializer Validation Errors
    elif isinstance(exc, ValidationError):
        msg = flatten_serializer_errors(exc.detail)
        msg = msg or "Validation Failed"
        return Response(
            default_response(msg=msg, error_code=ERR_CODES.VALIDATION_ERR),
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authorization Permission Exception
    elif isinstance(exc, PermissionDenied):
        res = default_response(msg="Permission Denied", error_code=ERR_CODES.API_KEY_ERR)
        res = response.data or res
        return Response(res, response.status_code)
    
    elif isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        msg = response.data.get('detail')
        msg = msg or "Authentication failed"
        return Response(
            default_response(msg=msg, error_code=ERR_CODES.INVALID_TOKEN_ERR), 
            status=response.status_code
        )
    
    # Any Known Response Category
    elif response is not None:
        detail = response.data.get("detail", None)
        msg = detail or "Error"
        return Response(
            default_response(msg=msg, error_code=getattr(exc, "error_code", ERR_CODES.INTERNAL_ERR)),
            status=response.status_code
        )
    
    logger.exception("HEADLESS_ERROR", data={"exc_info": exc})    

    return Response(default_response(), status=500)


class HeadlessException(APIException):
    status_code = 500
    default_detail = "Internal server error"
    default_code = ERR_CODES.INTERNAL_ERR