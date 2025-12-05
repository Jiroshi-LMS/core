import structlog
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework.exceptions import APIException
from ..constants import ERR_CODES

logger = structlog.get_logger(__name__)

def headless_exception_handler(exc, context):
    """
    Clean, consistent output for ALL headless errors.
    """
    response = exception_handler(exc, context)

    logger.exception("HEADLESS_ERROR", data={"exc_info": exc})    

    if response is not None:
        detail = response.data.get("detail", None)
        return Response({
            "status": False,
            "results": False,
            "message": detail or "Error",
            "data": None,
            "error_code": getattr(exc, "error_code", None),
        }, status=response.status_code)

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