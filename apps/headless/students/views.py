import structlog

from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.headless.common.constants import TokenTransportMode
from apps.headless.common.utilities.BaseView import HeadlessAPIView
from apps.headless.common.permissions.common import InstructorAPIKeyAuthentication, StudentJWTAuthentication, IsAuthenticatedStudent
from apps.headless.common.utilities import success, AuthError, InputValidationError
from apps.headless.common.helpers.request_helpers import get_refresh_transport_mode
from django.conf import settings
from django.contrib.auth.hashers import check_password
from rest_framework.permissions import AllowAny

from .serializers import (StudentPasswordAuthRequestSerializer, StudentLoginRequestSerializer,
                          StudentDetailsUpdateSerializer)
from .services import StudentAuthService


logger = structlog.get_logger(__name__)



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
            key="student_refresh_token",
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
            refresh_tok = request.COOKIES.get("student_refresh_token")
            
        if not refresh_tok: 
            raise AuthError("Refresh Token required !")
        student_toks = StudentAuthService.refresh_student_token(
            refresh_tok
        )
        return get_response(
            mode, 
            student_toks['access'], 
            student_toks['refresh']
        )
    

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
    

class StudentAccountDetailsUpdateView(HeadlessAPIView):
    """
    Student account details update
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    permission_classes = [IsAuthenticatedStudent]
    access_type = KEY_TYPES.get('pk')
    
    def put(self, request):
        serializer = StudentDetailsUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        if not check_password(validated_data.get('current_password'), request.student.password):
            raise InputValidationError("Provided current password is incorrect")
        StudentAuthService.updated_student_details(validated_data, request.student, request.instructor)
        return success(msg="Student account details updated !")
    

class StudentLogoutView(HeadlessAPIView):
    """
    Student Logout view.
    Will check if refresh token exists in cookies,
    and makes sure to remove them
    """
    authentication_classes = [InstructorAPIKeyAuthentication, StudentJWTAuthentication]
    permission_classes = [IsAuthenticatedStudent]
    access_type = KEY_TYPES.get('pk')

    def post(self, request):
        mode = get_refresh_transport_mode(request)
        refresh_tok = request.data.get('refresh_token')
        if mode == TokenTransportMode.COOKIE:
            refresh_tok = request.COOKIES.get("student_refresh_token")
        if not refresh_tok: 
            raise AuthError("Refresh Token required !")
        StudentAuthService.blacklist_token(refresh_tok)
        response = success(msg="Student logged out!")
        if mode == TokenTransportMode.COOKIE:
            response.delete_cookie(
                key="student_refresh_token",
                path="/",
            )
        return response
