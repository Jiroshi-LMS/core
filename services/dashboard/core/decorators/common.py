"""
Enhanced middleware for comprehensive logging and user activity tracking.
"""
from core.constants import CommonErrors
from core.helpers import flatten_serializer_errors
from core.utilities import Res
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status, serializers
import structlog
import traceback
import functools

logger = structlog.get_logger(__name__)

def handle_exceptions(view_func):
    @functools.wraps(view_func)
    def wrapper(self, request, *args, **kwargs):
        try:
            return view_func(self, request, *args, **kwargs)
        except ValueError as e:
            err_stack = traceback.format_exc()
            logger.error("value_error", error=str(e), extra={'path': request.path, 'stack': err_stack})
            return Res(status.HTTP_400_BAD_REQUEST, False, msg=str(e)).json()
        except serializers.ValidationError as e:
            flat_msg = flatten_serializer_errors(e.detail)
            logger.error(
                "serializer_validation_failed",
                error=flat_msg
            )
            return Res(status.HTTP_400_BAD_REQUEST, False, msg=flat_msg).json()
        except (ObjectDoesNotExist, Http404) as e:
            err_stack = traceback.format_exc()
            logger.error("object_not_found", error=str(e), extra={'path': request.path, 'stack': err_stack})
            return Res(status.HTTP_404_NOT_FOUND, False, msg="Not found").json()
        except IntegrityError as e:
            err_stack = traceback.format_exc()
            logger.error("integrity_error", error=str(e), extra={'path': request.path, 'stack': err_stack})
            return Res(status.HTTP_400_BAD_REQUEST, False, msg="Data Integrity Error").json()
        except Exception as e:
            err_stack = traceback.format_exc()
            logger.exception("unexpected_server_error", error=str(e), extra={'path': request.path, 'stack': err_stack})
            return Res(status.HTTP_500_INTERNAL_SERVER_ERROR, False, msg=CommonErrors.SERVER_ERR).json()

    return wrapper