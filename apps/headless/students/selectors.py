from apps.dashboard.instructors.models import Instructor
from apps.headless.students.models import Student


class StudentAuthSelector():

    @staticmethod
    def create_student(student_data: dict, instructor: Instructor):
        return Student.objects.create(
            identifier = student_data.get('identifier'),
            password = student_data.get('hashed_password'),
            instructor = instructor
        )
