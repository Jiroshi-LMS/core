from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.headless.common.constants import TokenTransportMode
from apps.headless.common.utilities.BaseView import HeadlessAPIView
from apps.headless.common.permissions.common import InstructorAPIKeyAuthentication, StudentJWTAuthentication, IsAuthenticatedStudent
from apps.headless.common.utilities import success, AuthError, InputValidationError
from apps.headless.common.helpers.request_helpers import get_refresh_transport_mode
from django.conf import settings
from rest_framework.permissions import AllowAny

from .serializers import (StudentPasswordAuthRequestSerializer, StudentLoginRequestSerializer)
from .services import StudentAuthService



def get_response(mode: str, access_tok: str, refresh_tok: str):
    """
    Returns response object with the appropriate
    form transport mode for refresh token.
    """

    response_msg="Tokens Generated !"
    if mode == TokenTransportMode.COOKIE:
        response = success({
            "access_token": access_tok,
        }, msg=response_msg)
        response.set_cookie(
            key="refresh_token",
            value=refresh_tok,
            httponly=True,
            secure=True,
            samesite="Lax",
            max_age=settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"].total_seconds()
        )
        return response
    
    return success(
        data={
            "access_token": access_tok, 
            "refresh_token": refresh_tok
        }, 
        msg=response_msg
    )


class StudentSignUpView(HeadlessAPIView):
    """
    Student signup
    """
    authentication_classes = [InstructorAPIKeyAuthentication]
    access_type = KEY_TYPES.get('pk')
    
    def post(self, request):
        mode = get_refresh_transport_mode(request)
        serializer = StudentPasswordAuthRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        student_toks = StudentAuthService.signup_student(validated_data, request.instructor)
        return get_response(
            mode, 
            student_toks['access'], 
            student_toks['refresh']
        )
    

class StudentLoginView(HeadlessAPIView):
    """
    Student Login
    """
    authentication_classes = [InstructorAPIKeyAuthentication]
    access_type = KEY_TYPES.get('pk')

    def post(self, request):
        mode = get_refresh_transport_mode(request)
        serializer = StudentLoginRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        student_toks = StudentAuthService.login_student(serializer.validated_data, request.instructor)
        return get_response(
            mode, 
            student_toks['access'], 
            student_toks['refresh']
        )
    

class StudentExistsLookup(HeadlessAPIView):
    """
    Quick lookup to check if identifier 
    is available under a given instructor
    """
    authentication_classes = [InstructorAPIKeyAuthentication]
    access_type = KEY_TYPES.get('pk')

    def get(self, request):
        identifier = request.query_params.get('identifier')
        if not identifier:
            raise InputValidationError("Identifier missing")
        exists = StudentAuthService.does_exist({"identifier": identifier})
        return success(data=exists, msg="Status fetched")


class StudentRefreshTokenView(HeadlessAPIView):
    """
    Student Refresh Token
    """
    permission_classes = [AllowAny]

    def post(self, request):
        mode = get_refresh_transport_mode(request)
        refresh_tok = request.data.get('refresh_token')
        if mode == TokenTransportMode.COOKIE:
            refresh_tok = request.COOKIES.get("refresh_token")
            
        if not refresh_tok: 
            raise AuthError("Refresh Token required !")
        student_toks = StudentAuthService.refresh_student_token(
            refresh_tok
        )
        return success(data=student_toks, msg="Student token refreshed !")
    

class StudentProfileView(HeadlessAPIView):
    """
    Profile lookup for student
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    permission_classes = [IsAuthenticatedStudent]
    access_type = KEY_TYPES.get('pk')

    def get(self, request):
        student = request.student
        return success(data={
            "uuid": student.uuid,
            "identifier": student.identifier,
        })