import bcrypt
import traceback

from apps.dashboard.apikeys.constants import KEY_SEPARATOR, KEY_TYPES
from apps.dashboard.apikeys.models import ApiKeys
from apps.dashboard.instructors.models import Instructor
from apps.headless.common.constants import ERR_CODES
from apps.headless.common.utilities import ServerError, InputValidationError, AuthError, NotFoundError
from apps.headless.students.models import Student
from datetime import timedelta
from django.core.cache import cache
from django.conf import settings
from django.db.models import Q
from django.utils import timezone
from django.utils import timezone
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend



API_KEY_CACHE_PREFIX = "api_key"
API_KEY_FALLBACK_TTL = 10 * 60  # 10 minutes



class InstructorAPIKeyAuthentication(BaseAuthentication):

    def authenticate(self, request):
        raw_key = request.headers.get("x-api-key")
        if not raw_key:
            raise AuthenticationFailed("API key missing")

        try:
            key_type, key_id, key_val = raw_key.split(KEY_SEPARATOR)
        except ValueError:
            raise AuthenticationFailed("Malformed API key")

        view = request.parser_context.get("view")
        access_type = getattr(view, "access_type", None)
        if not access_type:
            raise AuthenticationFailed("Permission misconfiguration")

        if KEY_TYPES.get(key_type) != access_type:
            raise AuthenticationFailed("Invalid API key type")
        
        cache_key = f"{API_KEY_CACHE_PREFIX}:{key_id}"
        cached = cache.get(cache_key)

        if cached:
            if cached["key_type"] != access_type:
                raise AuthenticationFailed("Invalid API key type")

            try:
                request.instructor = Instructor.objects.get(id=cached["instructor_id"])
                return None
            except Instructor.DoesNotExist:
                raise NotFoundError("Instructor not found")


        key = (
            ApiKeys.objects
            .select_related("instructor")
            .filter(
                Q(expires_at__isnull=True) | Q(expires_at__gte=timezone.now()),
                uuid=key_id,
                key_type=access_type,
            )
            .first()
        )

        if not key:
            raise AuthenticationFailed("Invalid or Expired API key")

        if not bcrypt.checkpw(
            key_val.encode("utf-8"),
            key.key_hash.encode("utf-8")
        ):
            raise AuthenticationFailed("Invalid API key")

        if key.expires_at:
            ttl = int((key.expires_at - timezone.now()).total_seconds())
            ttl = max(0, min(ttl, API_KEY_FALLBACK_TTL))
        else:
            ttl = API_KEY_FALLBACK_TTL

        cache.set(
            cache_key,
            {
                "instructor_id": key.instructor_id,
                "key_type": key.key_type,
            },
            timeout=ttl,
        )

        request.instructor = key.instructor
        return None


class StudentJWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return None  # optional unless permission demands it
        try:
            prefix, token = auth_header.split(" ")
        except ValueError:
            raise AuthenticationFailed("Invalid Authorization header")

        if prefix.lower() != "bearer":
            raise AuthenticationFailed("Invalid token prefix")

        backend = TokenBackend(
            algorithm=settings.SIMPLE_JWT.get("ALGORITHM", "HS256"),
            signing_key=settings.SIMPLE_JWT["SIGNING_KEY"],
        )

        try:
            payload = backend.decode(token, verify=True)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")

        student_id = payload.get("student_id")
        instructor_id = payload.get("instructor_id")
        print(payload)
        if not student_id or not instructor_id:
            raise AuthenticationFailed("Malformed token")

        request_instructor = getattr(request, "instructor", None)
        if not request_instructor:
            raise AuthenticationFailed("Instructor context missing")

        # HARD TENANT BOUNDARY
        if request_instructor.id != instructor_id:
            raise AuthenticationFailed("Instructor-token mismatch")

        try:
            student = Student.objects.get(
                id=student_id,
                instructor_id=request_instructor.id
            )
        except Student.DoesNotExist:
            raise AuthenticationFailed("Student not found")

        request.student = student
        return (student, None)
    

class IsAuthenticatedStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        if not bool(getattr(request, "student", None)):
            raise PermissionDenied(detail={
                "status": False,
                "results": False,
                "message": "Student not authenticated",
                "data": None,
                "error_code": ERR_CODES.INVALID_TOKEN_ERR
            })
        return True