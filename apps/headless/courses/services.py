from apps.dashboard.instructors.models import Instructor
from apps.dashboard.courses.models import Course, CourseLesson
from apps.core.utilities import S3Utils
from apps.core.constants import Units
from apps.headless.students.models import Student
from apps.headless.common.utilities.Errors import NotFoundError, RecordExistsError, ForbiddenError
from django.db import IntegrityError
from django.db.models.query import QuerySet

from .selectors import EnrollmentSelector, CourseSelector, CourseLessonSelector, LessonResourceSelector



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
    def get_course_lesson_queryset(course_uuid: str, instructor: Instructor, lesson_uuid: str | None = None):
        if lesson_uuid:
            return CourseLessonSelector.get_lesson_uuid_filtered(lesson_uuid, course_uuid, instructor)
        return CourseLessonSelector.get_all(course_uuid, instructor)
    
    @staticmethod
    def enrich_with_enrollment_status(base_lesson_queryset: QuerySet[CourseLesson], student: Student):
        return CourseLessonSelector.annotate_with_enrollment_status(base_lesson_queryset, student)
    

class LessonResourceServices:
    @staticmethod
    def get_lesson_resources(lesson: CourseLesson, instructor: Instructor):
        """
        Validates student's access to course, then fetches lesson resources
        """
        return LessonResourceSelector.get_resources_by_lesson(lesson, instructor)


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

    @staticmethod
    def get_enrolled_courses_list(student: Student, instructor: Instructor):
        return EnrollmentSelector.get_enrolled_courses(student, instructor)