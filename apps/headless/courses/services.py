from apps.dashboard.instructors.models import Instructor
from apps.dashboard.courses.models import Course
from apps.headless.courses.selectors import CourseSelector, CourseLessonSelector
from apps.headless.students.models import Student
from apps.headless.common.utilities.Errors import NotFoundError, RecordExistsError
from django.db import IntegrityError
from django.db.models.query import QuerySet

from .selectors import EnrollmentSelector



class CourseServices:
    """
    Service Layer for courses
    """
    @staticmethod
    def get_course_catalogue_queryset(instructor: Instructor, uuid: str | None = None):
        if uuid:
            return CourseSelector.get_uuid_filtered(uuid, instructor)
        return CourseSelector.get_all(instructor)
    
    @staticmethod
    def enrich_with_enrollment_status(base_course_queryset: QuerySet[Course], student: Student):
        return CourseSelector.annotate_with_enrollment_status(base_course_queryset, student)
    

class CourseLessonServices:
    """
    Service Layer for course lessons
    """
    @staticmethod
    def get_course_lesson_queryset(course_uuid: str, instructor: Instructor):
        return CourseLessonSelector.get_all(course_uuid, instructor)


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
