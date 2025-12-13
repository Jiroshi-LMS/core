from apps.dashboard.instructors.models import Instructor
from apps.dashboard.courses.models import Course
from apps.headless.students.models import Student
from apps.headless.courses.models import Enrollments


class CourseSelector:
    """
    Repo for Course selection.
    Creating a separate one for headless,
    as the dashboard one has different way of
    dealing with errors.
    """
    @staticmethod
    def get_by_uuid(course_uuid: str, instructor: Instructor):
        try:
            return Course.objects.get(uuid=course_uuid, created_by=instructor)
        except Course.DoesNotExist:
            return None
        

class EnrollmentSelector:
    """
    Repo for Enrollments
    """
    @staticmethod
    def create(student: Student, course: Course):
        return Enrollments.objects.create(
            student=student,
            course=course
        )
