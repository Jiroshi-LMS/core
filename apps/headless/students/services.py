from apps.headless.common.utilities.Errors import InputValidationError, NotFoundError, AuthError, RecordExistsError
from django.contrib.auth.hashers import make_password, check_password
from django.db import transaction, IntegrityError
from rest_framework_simplejwt.tokens import RefreshToken, TokenError

from .models import Student
from .selectors import Instructor, StudentSelector

class StudentAuthService():
    @staticmethod
    def get_auth_tokens(student: Student, instructor: Instructor):
        refresh = RefreshToken()
        refresh['student_id']=student.id
        refresh['student_identifier']=student.identifier
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
    def does_exist(lookups: dict):
        """
        Student Exists Quick Lookup. Unsure of the scope yet.
        Limited to identifier as of now
        """
        student_queryset = StudentSelector.lookup({"identifier": lookups.get('identifier')})
        if not student_queryset.first():
            return False
        return True


    @staticmethod
    def refresh_student_token(refresh_tok: str):
        """
        Student Token Refresh View 
        """
        try:
            refresh = RefreshToken(refresh_tok)
            access_token = str(refresh.access_token)

            payload = refresh.payload
            student_id = payload["student_id"]
            student_identifier = payload["student_identifier"]
            instructor_id = payload["instructor_id"]
        except (TokenError, KeyError):
            raise AuthError()
        
        # new_refresh_tok = str(refresh)  # half ass-ed refresh token rotation

        return {
            "access": access_token
            # "refresh": new_refresh
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
            return StudentAuthService.get_auth_tokens(student, instructor)
        except IntegrityError:
            raise RecordExistsError("Student with that information already exists !")
        

    @staticmethod
    def blacklist_token(refresh_tok: str):
        try:
            refresh = RefreshToken(refresh_tok)
            refresh.blacklist()
        except (TokenError, KeyError):
            raise AuthError()