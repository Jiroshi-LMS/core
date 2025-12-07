import traceback
from apps.dashboard.instructors.models import Instructor
from apps.headless.students.models import Student


class StudentSelector():

    @staticmethod
    def create_student(student_data: dict, instructor: Instructor):
        return Student.objects.create(
            identifier = student_data.get('identifier'),
            password = student_data.get('hashed_password'),
            instructor = instructor
        )
    
    @staticmethod
    def get_by_identifier(identifier: str, instructor: Instructor):
        try:
            return Student.objects.get(identifier=identifier, instructor=instructor)
        except Student.DoesNotExist as e:
            return None
