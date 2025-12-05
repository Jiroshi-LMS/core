"""
Enhanced middleware for comprehensive logging and user activity tracking.
"""
from apps.core.constants import CommonErrors
from apps.core.helpers import flatten_serializer_errors, extract_integrity_error_context
from apps.core.utilities import Res
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError
from django.http import Http404
from rest_framework import status, serializers
from rest_framework.exceptions import PermissionDenied
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
        except PermissionDenied as e:
            err_stack = traceback.format_exc()
            logger.error("permission_denied", error=str(e), extra={'path': request.path, 'stack': err_stack})
            return Res(status.HTTP_403_FORBIDDEN, False, msg=str(e)).json()
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
            msg=str(e)
            user_msg=extract_integrity_error_context(msg)
            logger.error("integrity_error", error=msg, extra={'path': request.path, 'stack': err_stack})
            return Res(status.HTTP_400_BAD_REQUEST, False, msg=user_msg).json()
        except Exception as e:
            err_stack = traceback.format_exc()
            logger.exception("unexpected_server_error", error=str(e), extra={'path': request.path, 'stack': err_stack})
            return Res(status.HTTP_500_INTERNAL_SERVER_ERROR, False, msg=CommonErrors.SERVER_ERR).json()

    return wrapper