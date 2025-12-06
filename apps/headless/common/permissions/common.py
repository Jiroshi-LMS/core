import bcrypt
import traceback

from apps.dashboard.apikeys.constants import KEY_SEPARATOR, KEY_TYPES
from apps.dashboard.apikeys.models import ApiKeys
from apps.headless.common.constants import ERR_CODES
from django.db.models import Q
from django.utils import timezone
from apps.dashboard.instructors.models import Instructor
from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied



class IsValidInstructor(permissions.BasePermission):
    """
    For Validating Instructor's api key
    for headless APIs only.
    """

    def _permission_denied(
            self, 
            msg: str = "Invalid or Expired API Key !",
            error_code: str = ERR_CODES.API_KEY_ERR
    ):
        return PermissionDenied(detail={
            "status": False,
            "results": False,
            "message": msg,
            "data": None,
            "error_code": error_code
        })

    def _validate_instructor(
            self, 
            raw_key: str, 
            access_type: str
    ) -> Instructor | None:
        """
        Helper function for facilitating validation
        """
        try:
            api_key = raw_key.split(KEY_SEPARATOR);
            if len(api_key) != 3:
                return None
            key_type, key_id, key_val = api_key

            request_key = KEY_TYPES.get(key_type, None)
            if not request_key or request_key != access_type:
                return None
            
            key = (ApiKeys.objects
                .select_related('instructor')
                .filter(
                    Q(expires_at__isnull=True) | 
                    Q(expires_at__gte=timezone.now()),
                    uuid=key_id,
                    key_type=access_type,
                )
            ).first()
            if not key or not bcrypt.checkpw(key_val.encode("utf-8"), key.key_hash.encode("utf-8")):
                return None
            
            return key.instructor
        except Exception:
            traceback.print_exc()
            return None
        
    def has_permission(self, request, view):
        access_type = getattr(view, "access_type", None)    # public/private
        raw_key = request.headers.get('x-api-key');
        if not access_type:
            raise self._permission_denied("Permission Misconfiguration !", ERR_CODES.INTERNAL_ERR)
        if not raw_key:
            raise self._permission_denied()
        instructor = self._validate_instructor(raw_key, access_type)
        if not instructor:
            raise self._permission_denied()
        request.instructor = instructor
        return True