import bcrypt
import traceback

from apps.dashboard.apikeys.constants import KEY_SEPARATOR, KEY_TYPES
from apps.dashboard.apikeys.models import ApiKeys
from apps.dashboard.instructors.models import Instructor
from apps.headless.common.constants import ERR_CODES
from apps.headless.common.utilities import ServerError, InputValidationError, AuthError
from apps.headless.students.models import Student
from django.db.models import Q
from django.utils import timezone
from django.conf import settings
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.backends import TokenBackend



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
        """
        Helper function to generate
        permission denied errors
        """

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
        except Exception as e:
            traceback.print_exc()
            return None
        
    def has_permission(self, request, view):
        """
        API Key validation check
        """
        access_type = getattr(view, "access_type", None)    # public/private
        raw_key = request.headers.get('x-api-key');
        if not access_type:
            raise self._permission_denied("Permission Misconfiguration !", ERR_CODES.INTERNAL_ERR)
        if not raw_key:
            raise self._permission_denied()
        instructor = self._validate_instructor(raw_key, access_type)
        if not instructor:
            x = self._permission_denied()
            print(str(x))
            raise x
        request.instructor = instructor
        return True


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