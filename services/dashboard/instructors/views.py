import structlog
import traceback

from core.constants import ENV, CommonErrors
from core.decorators import handle_exceptions
from core.utilities import Res
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView

from .models import Instructor
from .serializers import InstructorSerializer, InstructorLoginSerializer
from .selectors import InstructorSelector


logger = structlog.get_logger(__name__)
instructor_selector = InstructorSelector()
    

class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
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
    

    @action(detail=False, methods=['POST'], url_path='login')
    @handle_exceptions
    def login_view(self, request, *args, **kwargs):
        """
            Instructor Login
        """
        serializer = InstructorLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instructor = instructor_selector.get_by_username_or_email(serializer.validated_data['username'])
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
        

class LogoutInstructorView(APIView):
    """
    Logout instructor view.
    """
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request, *args, **kwargs):
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