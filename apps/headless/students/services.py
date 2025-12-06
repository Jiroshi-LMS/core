from .selectors import Instructor, StudentAuthSelector


class StudentAuthService():
    @staticmethod
    def signup_user(student_data: dict, instructor: Instructor):
        return StudentAuthSelector.create_user(student_data, instructor)
