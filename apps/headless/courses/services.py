from apps.dashboard.instructors.models import Instructor
from apps.headless.courses.selectors import CourseSelector
from apps.headless.students.models import Student
from apps.headless.common.utilities.Errors import NotFoundError, RecordExistsError
from django.db import IntegrityError

from .selectors import EnrollmentSelector



class CourseEnrollmentService:
    """
    Service for managing Enrollments
    """
    @staticmethod
    def enroll_student(student: Student, course_uuid: str, instructor: Instructor):
        course = CourseSelector.get_by_uuid(course_uuid, instructor)
        if not course: raise NotFoundError("Student not found !")

        try:
            return EnrollmentSelector.create(student, course)
        except IntegrityError:
            raise RecordExistsError("Student already enrolled !")
