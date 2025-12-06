from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken

from .selectors import Instructor, StudentAuthSelector


class StudentAuthService():
    @staticmethod
    def signup_student(student_data: dict, instructor: Instructor):
        student_data['hashed_password'] = make_password(student_data['password'])
        student = StudentAuthSelector.create_student(student_data, instructor)
        refresh = RefreshToken()
        refresh['student_id']=student.id
        refresh['student_identifier']=student.identifier

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh)
        }
