from apps.dashboard.instructors.models import Instructor
from apps.dashboard.courses.models import Course
from apps.headless.students.models import Student
from apps.headless.courses.models import Enrollments
from django.db.models import Exists, OuterRef, Value, BooleanField
from django.db.models.query import QuerySet


class CourseSelector:
    """
    Repo for Course selection.
    Creating a separate one for headless,
    as the dashboard one has different way of
    dealing with errors.
    """
    @staticmethod
    def get_all(instructor: Instructor):
        return Course.objects.filter(created_by=instructor, access_status="active")
    
    @staticmethod
    def get_uuid_filtered(uuid, instructor):
        return Course.objects.filter(uuid=uuid, created_by=instructor, access_status="active")
    
    @staticmethod
    def get_by_uuid(course_uuid: str, instructor: Instructor):
        try:
            return Course.objects.get(uuid=course_uuid, created_by=instructor)
        except Course.DoesNotExist:
            return None
        
    @staticmethod
    def annotate_with_enrollment_status(base_queryset: QuerySet[Course], student: Student):
        if not student:
            return base_queryset.annotate(
                is_enrolled=Value(False, output_field=BooleanField())
            )
        return base_queryset.annotate(
            is_enrolled=Exists(
                Enrollments.objects.filter(
                    student_id=student.id,
                    course_id=OuterRef('id')
                )
            )
        )
        

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
