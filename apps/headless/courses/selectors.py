from apps.dashboard.instructors.models import Instructor
from apps.dashboard.courses.models import Course, CourseLesson, LessonResource
from apps.headless.students.models import Student
from apps.headless.courses.models import Enrollments
from django.db.models import Exists, OuterRef, Value, BooleanField
from django.db.models.query import QuerySet


class CourseSelector:
    """
    Repo for Course selection.
    Creating a separate one for headless,
    as the dashboard one has different control flow.
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
    

class CourseLessonSelector:
    """
    Repo for Course lesson selection.
    Creating a separate one for headless,
    as the dashboard one has different control flow.
    """
    @staticmethod
    def get_all(course_uuid: str, instructor: Instructor):
        return CourseLesson.objects.filter(
            course__uuid=course_uuid,
            created_by=instructor,
            access_status="active"
        )
    
    @staticmethod
    def get_lesson_uuid_filtered(lesson_uuid: str, course_uuid: str, instructor: Instructor):
        return CourseLesson.objects.select_related('course').filter(
            uuid=lesson_uuid,
            course__uuid=course_uuid,
            created_by=instructor,
            access_status="active"
        )
    
    @staticmethod
    def annotate_with_enrollment_status(base_queryset: QuerySet[CourseLesson], student: Student):
        if not student:
            return base_queryset.annotate(
                is_enrolled=Value(False, output_field=BooleanField())
            )
        return base_queryset.annotate(
            is_enrolled=Exists(
                Enrollments.objects.filter(
                    student=student.id,
                    course_id=OuterRef('course_id')
                )
            )
        )


class LessonResourceSelector:
    """
    Repo for lesson resource
    """
    @staticmethod
    def get_resources_by_lesson(lesson: CourseLesson, instructor: Instructor):
        return LessonResource.objects.filter(lesson=lesson, created_by=instructor)
        

class EnrollmentSelector:
    """
    Repo for Enrollments
    """
    @staticmethod
    def get_all(instructor: Instructor):
        return Enrollments.objects.filter(
            course__created_by=instructor
        )

    @staticmethod
    def create(student: Student, course: Course):
        return Enrollments.objects.create(
            student=student,
            course=course
        )
    
    @staticmethod
    def get_enrolled_courses(student: Student, instructor: Instructor):
        return Enrollments.objects.select_related('course').filter(
            student=student, 
            course__created_by=instructor, 
            course__access_status='active'
        )