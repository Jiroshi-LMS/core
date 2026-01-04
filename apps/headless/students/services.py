import structlog
from apps.headless.common.utilities.Errors import InputValidationError, NotFoundError, AuthError, RecordExistsError
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction, IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from .models import Student
from .serializers import StudentTokenRefreshSerializer
from .selectors import Instructor, StudentSelector

logger = structlog.get_logger("jiroshi").bind(
    module=__name__
)

class StudentAuthService():
    @staticmethod
    def get_auth_tokens(student: Student, instructor: Instructor):
        refresh = RefreshToken()
        refresh['student_id']=student.id
        refresh['instructor_id']=instructor.id

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }

    @staticmethod
    def signup_student(student_data: dict, instructor: Instructor):
        """
        Student Signup Service
        """
        student_data['hashed_password'] = make_password(student_data['password'])
        try:
            student = StudentSelector.create_student(student_data, instructor)
            return StudentAuthService.get_auth_tokens(student, instructor)
        except IntegrityError:
            raise RecordExistsError("Student account already exists !")

    @staticmethod
    def login_student(student_data: dict, instructor: Instructor):
        """
        Student Login Service
        """
        student = StudentSelector.get_by_identifier(student_data.get('identifier'), instructor)
        if not student: raise NotFoundError("Student not found !")

        if not check_password(student_data.get('password'), student.password):
            raise InputValidationError("Invalid identifier or password !")

        return StudentAuthService.get_auth_tokens(student, instructor)
    
    @staticmethod
    def does_identifier_exist(lookups: dict):
        """
        Quick Lookup to check if student identifier exists.
        """
        student_queryset = StudentSelector.lookup({"identifier": lookups.get('identifier')})
        if not student_queryset.first():
            return False
        return True

    @staticmethod
    def refresh_student_token(refresh_tok: str):
        """
        Always rotates refresh token.
        """
        print("REFRESH_TOK_SERVICE\n\n\n\n", refresh_tok)
        logger.info("REFRESH_TOK_SERVICE", data={"TEST": "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", "refresh_tok": refresh_tok})
        try:
            print("REFRESH_TOK_SERVICE_TRY\n\n\n\n", refresh_tok)
            logger.info("REFRESH_TOK_SERVICE_TRY", data={"TEST": "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", "refresh_tok": refresh_tok})
            serializer = StudentTokenRefreshSerializer(
                data={"refresh": refresh_tok}
            )
            print("AFTER_SERIALIZER\n\n\n\n", refresh_tok)
            logger.info("AFTER_SERIALIZER", data={"TEST": "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", "refresh_tok": refresh_tok})
        
            serializer.is_valid(raise_exception=True)
        except (TokenError, InvalidToken) as e:
            print("REFRESH_TOK_SERVICE_CATCH\n\n\n\n", refresh_tok)
            logger.info("REFRESH_TOK_SERVICE_CATCH", data={"TEST": "MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM", "refresh_tok": refresh_tok})
            raise AuthError("Invalid or expired refresh token")

        data = serializer.validated_data

        return {
            "access": data["access"],
            "refresh": data["refresh"],
        }
    
    @staticmethod
    def updated_student_details(validated_data: dict, student: Student, instructor: Instructor):
        """
        Method to update student details
        """
        try:
            with transaction.atomic():
                for key, value in validated_data.items():
                    if key == 'password':
                        value = make_password(value)
                    setattr(student, key, value)
                student.save()
            return student
        except IntegrityError:
            raise RecordExistsError("Student with that information already exists !")
        

    @staticmethod
    def blacklist_token(refresh_tok: str):
        try:
            refresh = RefreshToken(refresh_tok)
            refresh.blacklist()
        except (TokenError, KeyError):
            raise AuthError()