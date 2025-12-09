import traceback
from apps.dashboard.instructors.models import Instructor
from apps.headless.students.models import Student


class StudentSelector():
    """
    Student management repository layer
    """
    @staticmethod
    def create_student(student_data: dict, instructor: Instructor):
        """
        Creation call
        """
        return Student.objects.create(
            identifier = student_data.get('identifier'),
            password = student_data.get('hashed_password'),
            instructor = instructor
        )
    
    @staticmethod
    def lookup(lookup_dict: dict):
        """
        Quick lookup, unsure of the scope yet.
        Works with just identifier as of now.
        """
        lookup_filters = {}
        for key in lookup_dict.keys():
            lookup_filters[key] = lookup_dict.get(key)

        return Student.objects.filter(**lookup_filters)
    
    @staticmethod
    def get_by_identifier(identifier: str, instructor: Instructor):
        """
        Get student by identifier
        """
        try:
            return Student.objects.get(identifier=identifier, instructor=instructor)
        except Student.DoesNotExist as e:
            return None
