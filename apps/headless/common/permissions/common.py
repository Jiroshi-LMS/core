import bcrypt
import traceback

from apps.dashboard.apikeys.constants import KEY_SEPARATOR, KEY_TYPES
from apps.dashboard.apikeys.models import ApiKeys
from apps.dashboard.instructors.models import Instructor
from apps.headless.common.constants import ERR_CODES
from apps.headless.common.utilities import ServerError, InputValidationError
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
    

class StudentJWTAuthentication(BaseAuthentication):
    """
    Authenticates student using JWT access token.
    """

    def _extract_auth_header(self, request):
        """
        Get token from auth header
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            raise InputValidationError("Missing authorization token")
        try:
            prefix, token = auth_header.split(" ")
            if prefix.lower() != "bearer":
                raise InputValidationError("Invalid token prefix")
        except ValueError:
            raise AuthenticationFailed("Invalid Authorization header")
        
        return token
    
    def _extract_token_payload(self, token):
        """
        Extract auth token payload
        """
        try:
            backend = TokenBackend(
                algorithm=settings.SIMPLE_JWT["ALGORITHM"],
                signing_key=settings.SIMPLE_JWT["SIGNING_KEY"]
            )
            payload = backend.decode(token, verify=True)
        except Exception:
            raise AuthenticationFailed("Invalid or expired token")
        
        student_id = payload.get("student_id")
        instructor_id = payload.get("instructor_id")
        if not student_id or not instructor_id:
            raise AuthenticationFailed("Malformed token")
        
        return student_id, instructor_id
    
    def _instructor_validations(self, request, instructor_id):
        """
        Validate request instructor object against 
        student auth token payload instructor id
        """
        request_instructor = getattr(request, 'instructor', None)
        request_instructor_id = getattr(request_instructor, 'id', None)
        if not request_instructor or not request_instructor_id:
            raise ServerError("Instructor permission misconfiguration")
        
        if request_instructor_id != instructor_id:
            raise AuthenticationFailed("API key and Token Mismatch")
        
    def _get_student(self, student_id, instructor_id):
        """
        Student fetching DB Call
        """
        try:
            student = Student.objects.get(
                id=student_id,
                instructor_id=instructor_id
            )
            return student
        except Student.DoesNotExist:
            raise AuthenticationFailed("Student not found")

    def authenticate(self, request):
        """
        Main authentication function
        """
        token = self._extract_auth_header(request)
        student_id, instructor_id = self._extract_token_payload(token)
        self._instructor_validations(self, request, instructor_id)
        student = self._get_student(student_id, instructor_id)
        request.student = student
        return (student, None)