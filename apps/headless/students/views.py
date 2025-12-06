from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.headless.common.utilities.BaseView import HeadlessAPIView
from apps.headless.common.permissions.common import IsValidInstructor
from apps.headless.common.utilities import success

from .serializers import (SignUpRequestSerializer, )
from .services import StudentAuthService

class StudentSignUpView(HeadlessAPIView):
    permission_classes = [IsValidInstructor]
    access_type = KEY_TYPES.get('pk')
    
    def post(self, request):
        serializer = SignUpRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        student_toks = StudentAuthService.signup_student(validated_data, request.instructor)
        return success(data=student_toks, msg="Student Added !", code=201)
