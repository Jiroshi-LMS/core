import structlog
import traceback

from core.constants import ENV, CommonErrors
from core.decorators import handle_exceptions
from core.utilities import Res, S3Utils
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import viewsets, status
from rest_framework.decorators import action, permission_classes, parser_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Instructor
from .serializers import (
    InstructorSerializer, 
    InstructorLoginSerializer,
    InstructorInfoUpdateSerializer,
    InstructorProfileSerializer
)
from .selectors import InstructorSelector


logger = structlog.get_logger(__name__)
instructor_selector = InstructorSelector()
    

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.select_related('profile').all()
    serializer_class = InstructorSerializer

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Instructor Signup
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instructor = instructor_selector.create_instructor(serializer.validated_data)

        refresh = RefreshToken.for_user(instructor)
        refresh['instructor_id'] = instructor.id
        refresh['instructor_username'] = instructor.username
        refresh['instructor_email'] = instructor.email
        access = refresh.access_token

        logger.info(
            "instructor_signup_completed",
            instructor_id=str(instructor.id),
            username=instructor.username,
        )

        return Res(
            status.HTTP_201_CREATED, True, 
            data={
                'instructor_id': instructor.uuid,
                'access_token': str(access),
            },
            msg="Instructor created successfully."
        ).json_with_cookies({
            'key': 'instructor_refresh_token',
            'value': str(refresh),
            'expiry_seconds': ENV.REFRESH_TOKEN_EXP * 24 * 60 * 60
        })
    

    @handle_exceptions
    @action(detail=False, methods=['POST'], url_path='login')
    def login_view(self, request, *args, **kwargs):
        """
            Instructor Login
        """
        serializer = InstructorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instructor = instructor_selector.get_by_username_or_email(serializer.validated_data['email'])
        if not instructor.check_password(serializer.validated_data['password']):
            return Res(
                status.HTTP_401_UNAUTHORIZED, False, 
                msg="Invalid credentials."
            ).json()
        
        refresh = RefreshToken.for_user(instructor)
        refresh['instructor_id'] = instructor.id
        refresh['instructor_username'] = instructor.username
        refresh['instructor_email'] = instructor.email
        access = refresh.access_token
        
        logger.info(
            "instructor_login_completed",
            instructor_id=str(instructor.id),
            username=instructor.username,
        )
        
        return Res(
            status.HTTP_200_OK, True, 
            data={
                'instructor_id': instructor.uuid,
                'access_token': str(access),
            },
            msg="Instructor logged in successfully."
        ).json_with_cookies({
            'key': 'instructor_refresh_token',
            'value': str(refresh),
            'expiry_seconds': ENV.REFRESH_TOKEN_EXP * 24 * 60 * 60
        })
    
    @handle_exceptions
    @action(detail=False, methods=['POST'], url_path='profile', permission_classes=[IsAuthenticated])
    def set_profile(self, request, *args, **kwargs):
        """
            Set Instructor Profile
        """
        instructor = instructor_selector.get_by_id(request.user.id)
        serializer = InstructorProfileSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        def all_profile_data_exists(profile_data):
            for value in profile_data.values():
                if not value:
                    return False
            return True

        profile_completion = 'complete'
        if not instructor.phone_number or not all_profile_data_exists(validated_data):
            profile_completion = 'partial'

        try:
            profile = instructor_selector.get_profile(instructor)
        except ObjectDoesNotExist:
            profile = None

        is_profile_picture_valid = validated_data.get('profile_picture') != None and validated_data.get('profile_picture') != ""
        if profile and profile.profile_picture and is_profile_picture_valid:
            S3Utils.delete_via_object_key(object_keys=[profile.profile_picture], bucket_name=ENV.S3_STATIC_BUCKET)

        with transaction.atomic():
            profile, created = instructor_selector.create_update_profile(instructor, validated_data, is_profile_picture_valid)
            instructor.profile_completion_status = profile_completion
            instructor.save()
        
        return Res(
            status.HTTP_200_OK, True, 
            data={
                'instructor_id': instructor.uuid,
                'profile_id': profile.uuid,
                'is_created': created,
            },
            msg="Instructor profile updated successfully."
        ).json()
    

    @handle_exceptions
    @action(detail=False, methods=['GET'], url_path='me', permission_classes=[IsAuthenticated])
    def get_profile(self, request, *args, **kwargs):
        serializer = self.get_serializer(request.user)
        return Res(
            code=status.HTTP_200_OK,
            data=serializer.data,
            msg="Instructor retrieved successfully."
        ).json()

    
    @handle_exceptions
    @action(detail=False, methods=['POST'], url_path='logout', permission_classes=[IsAuthenticated])
    def logout_view(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('instructor_refresh_token')
        if not refresh_token:
            return Res(
                status.HTTP_401_UNAUTHORIZED, False, 
                msg=CommonErrors.TOKEN_EXPIRED
            ).json()
        
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
            response = Res(
                status.HTTP_200_OK, True,
                msg="Logged out successfully."
            ).json()
            response.delete_cookie('instructor_refresh_token')
            return response

        except Exception as e:
            traceback_str = traceback.format_exc()
            logger.error(
                "instructor_logout_failed",
                error=str(e),
                log_type="error",
                extra={'stack': traceback_str}
            )
            response = Res(
                status.HTTP_400_BAD_REQUEST, False,
                msg="Invalid refresh token."
            ).json()
            response.delete_cookie('instructor_refresh_token')
            return response
    
    @handle_exceptions
    @action(detail=False, methods=['PUT'], url_path='update-info', permission_classes=[IsAuthenticated])
    def update_info(self, request, *args, **kwargs):
        serializer = InstructorInfoUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instructor = instructor_selector.get_by_id(request.user.id)
        instructor_selector.update_info(instructor, serializer.validated_data)

        return Res(
            status.HTTP_200_OK, True, 
            data=serializer.validated_data,
            msg="Instructor updated successfully."
        ).json()
    
    @handle_exceptions
    @action(detail=False, methods=['PATCH'], url_path='update-password', permission_classes=[IsAuthenticated])
    def update_password(self, request, *args, **kwargs):
        instructor = instructor_selector.get_by_id(request.user.id)
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Missing required fields."
            ).json()

        if not instructor.check_password(current_password):
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Provided current password is incorrect."
            ).json()
        instructor.set_password(new_password)
        instructor.save()
        return Res(
            status.HTTP_200_OK, True, 
            msg="Instructor's password updated successfully."
        ).json()
    

class CustomTokenRefreshView(TokenRefreshView):
    """
    Custom token refresh view to allow refreshing of instructor tokens.
    """
    serializer_class = TokenRefreshSerializer

    @handle_exceptions
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('instructor_refresh_token')
        if not refresh_token:
            return Res(
                status.HTTP_401_UNAUTHORIZED, False, 
                msg=CommonErrors.TOKEN_EXPIRED
            ).json()
        
        try:
            refresh = RefreshToken(refresh_token)
            instructor = instructor_selector.get_by_id(refresh['instructor_id'])

            access = refresh.access_token
            new_refresh = refresh

            return Res(
                status.HTTP_200_OK, True, 
                data={
                    'instructor_id': instructor.uuid,
                    'access_token': str(access),
                },
                msg="Instructor token refreshed successfully."
            ).json_with_cookies({
                'key': 'instructor_refresh_token',
                'value': str(new_refresh),
                'expiry_seconds': ENV.REFRESH_TOKEN_EXP * 24 * 60 * 60
            })
        except RefreshToken.DoesNotExist:
            return Res(
                status.HTTP_401_UNAUTHORIZED, False, 
                msg=CommonErrors.TOKEN_EXPIRED
            ).json()