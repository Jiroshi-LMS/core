import bcrypt
import traceback

from apikeys.constants import KEY_SEPARATOR, KeyTypes
from apikeys.models import ApiKeys
from django.db.models import Q
from django.utils import timezone
from instructors.models import Instructor
from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        field = obj.owner_field
        return getattr(obj, field) == request.user
    

class IsInstructor(permissions.BasePermission):
    def __init__(self, access_type: str):
        access_key = getattr(KeyTypes, access_type)
        if not access_key:
            raise KeyError("Invalid Permission Key")
        self.access_type = access_type  # public/private
        self.access_key = access_key    # pk/sk

    def _validate_instructor(self, raw_key: str) -> Instructor | None:
        api_key = raw_key.split(KEY_SEPARATOR);
        if len(api_key) != 3:
            return None
        key_type, key_id, key_val = api_key
        if (key_type != self.access_key):
            return None
        
        key = (ApiKeys.objects
            .select_related('instructor')
            .filter(
                Q(expires_at__isnull=True) | 
                Q(expires_at__gte=timezone.now()),
                uuid=key_id, 
                key_type=self.access_type,
            )
        ).first()
        if not key and not not bcrypt.checkpw(key_val, key.key_hash):
            return None
        
        return key.instructor
    
    def has_permission(self, request, view):
        try:
            raw_key = request.headers.get('x-api-key');
            if not raw_key:
                return False
            instructor = self._validate_instructor(raw_key)
            if not instructor:
                return False
            request.instructor = instructor
            return True
        except Exception as e:
            traceback.print_exc()
            return False