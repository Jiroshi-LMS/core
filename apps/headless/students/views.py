from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.headless.common.utilities.BaseView import HeadlessAPIView
from apps.headless.common.permissions.common import IsValidInstructor
from apps.headless.common.utilities import success

from .serializers import (StudentPasswordAuthRequestSerializer, StudentLoginRequestSerializer)
from .services import StudentAuthService

class StudentSignUpView(HeadlessAPIView):
    """
    Student signup
    """

    permission_classes = [IsValidInstructor]
    access_type = KEY_TYPES.get('pk')
    
    def post(self, request):
        serializer = StudentPasswordAuthRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        student_toks = StudentAuthService.signup_student(validated_data, request.instructor)
        return success(data=student_toks, msg="Student Added !", code=201)
    

class StudentLoginView(HeadlessAPIView):
    """
    Student Login
    """

    permission_classes = [IsValidInstructor]
    access_type = KEY_TYPES.get('pk')

    def post(self, request):
        serializer = StudentLoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student_toks = StudentAuthService.login_student(serializer.validated_data, request.instructor)
        return success(data=student_toks, msg="Student Logged-in !")
    

class StudentRefreshTokenView(HeadlessAPIView):
    """
    Student Login
    """

    permission_classes = [IsValidInstructor]
    access_type = KEY_TYPES.get('pk')

    def post(self, request):
        refresh_tok = request.data.get('refresh_token')
        
        student_toks = StudentAuthService.refresh_student_token(refresh_tok, request.instructor)
        return success(data=student_toks, msg="Student token refreshed !")