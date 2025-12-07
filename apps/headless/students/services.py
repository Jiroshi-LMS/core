from apps.headless.common.utilities.Errors import InputValidationError, NotFoundError
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken

from .selectors import Instructor, StudentSelector


class StudentAuthService():
    @staticmethod
    def signup_student(student_data: dict, instructor: Instructor):
        student_data['hashed_password'] = make_password(student_data['password'])
        student = StudentSelector.create_student(student_data, instructor)
        refresh = RefreshToken()
        refresh['student_id']=student.id
        refresh['student_identifier']=student.identifier

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }

    @staticmethod
    def login_student(student_data: dict, instructor: Instructor):
        student = StudentSelector.get_by_identifier(student_data.get('identifier'), instructor)
        if not student: raise NotFoundError("Student not found !")

        if not check_password(student_data.get('password'), student.password):
            raise InputValidationError("Invalid identifier or password !")

        refresh = RefreshToken()
        refresh['student_id']=student.id
        refresh['student_identifier']=student.identifier

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
        

    @staticmethod
    def refresh_student_token(refresh_tok: str, instructor):
        pass
