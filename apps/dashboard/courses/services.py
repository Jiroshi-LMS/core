from apps.core.constants import ENV, Units
from apps.core.utilities import S3Utils
from django.db import transaction
from django.db.models import Sum

from .models import Instructor, Course, CourseLesson, LessonResource
from .selectors import (
    CourseSelector,
    LessonSelector,
    LessonResourceSelector
)



lesson_selector = LessonSelector()
resource_selector = LessonResourceSelector()


class CourseServices:

    @staticmethod
    def create(validated_data: dict, instructor: Instructor) -> Course:
        return CourseSelector.create(validated_data, instructor)
    
    @staticmethod
    def validate_lesson_count_for_toggle(course: Course, instructor: Instructor):
        lesson_count = lesson_selector.active_lessons(course, instructor).count()
        if lesson_count < 1:
            raise ValueError("Can't set course as active without any lessons.")

    @staticmethod
    def toggle_activation(course: Course, instructor: Instructor) -> Course:
        if course.access_status == 'active':
            course.access_status = 'inactive'
        else:
            CourseServices.validate_lesson_count_for_toggle(course, instructor)
            course.access_status = 'active'
        course.save()
        return course
    
    @staticmethod
    def update_course_info(validated_data: dict, course: Course, instructor: Instructor) -> Course:
        with transaction.atomic():
            if validated_data.get('thumbnail') and course.thumbnail != validated_data.get('thumbnail'):
                S3Utils.delete_via_object_key(
                    object_keys=[course.thumbnail],
                    bucket_name=ENV.S3_STATIC_BUCKET
                )
            if validated_data.get('access_status'):
                access_status_string = 'active'
            else:
                access_status_string = 'inactive' if course.access_status in ['active', 'inactive'] else 'draft'
            if access_status_string == 'active':
                CourseServices.validate_lesson_count_for_toggle(course, instructor)
            validated_data['access_status'] = access_status_string
            return CourseSelector.update(validated_data, course)

    @staticmethod
    def soft_delete_course(course: Course, instructor: Instructor):
        with transaction.atomic():
            lessons = lesson_selector.all_lessons(course, instructor)
            course.delete()
            for lesson in lessons:
                lesson.delete()


class CourseLessonServices:
    @staticmethod
    def create(validated_data: dict, instructor: Instructor) -> CourseLesson:
        course = CourseSelector.by_uuid(validated_data['course_uuid'], instructor)
        return lesson_selector.create(
            validated_data, instructor, course
        )
    
    @staticmethod
    def update_lesson(validated_data: dict, lesson: CourseLesson):
        if validated_data.get('access_status'):
            access_status_string = 'active'
        else:
            access_status_string = 'inactive' if lesson.access_status in ['active', 'inactive'] else 'draft'
        if access_status_string == 'active' and lesson.media_key == None:
            raise ValueError("Can't set lesson as active, video has not been uploaded yet!")
        validated_data['access_status'] = access_status_string
        lesson = lesson_selector.update(validated_data, lesson)
    
    @staticmethod
    def update_lesson_media(
        lesson_media: str, 
        media_duration: float,
        media_size: int,
        lesson: CourseLesson, 
        instructor: Instructor
    ) -> tuple[CourseLesson, Course]:
        existing_media_key = lesson.media_key
        if existing_media_key and existing_media_key != lesson_media:
            S3Utils.delete_via_object_key(object_keys=[existing_media_key])
        lesson.media_key = lesson_media
        lesson.duration = media_duration
        lesson.media_size=media_size
        if lesson.access_status == 'draft':
            lesson.access_status = 'active'
        lesson.save()

        course = CourseSelector.by_uuid(lesson.course.uuid, instructor)
        course_lessons_duration = lesson_selector.active_lessons(course, instructor).aggregate(
            duration=Sum('duration')
        )['duration']
        if course_lessons_duration is not None and course_lessons_duration > 0:
            course.duration = course_lessons_duration
            if course.access_status == 'draft':
                course.access_status = 'inactive'
            course.save()
        return lesson, course

    @staticmethod
    def soft_delete_lesson(lesson: CourseLesson, instructor: Instructor):
        course = CourseSelector.by_id(lesson.course_id, instructor)
        course.duration = course.duration - lesson.duration
        if course.duration <= 0:
            course.duration = 0
            course.access_status = 'draft'
        course.save()
        lesson.delete()


class LessonResourceServices:
    
    @staticmethod
    def create(validated_data: dict, instructor: Instructor) -> tuple[LessonResource, CourseLesson]:
        lesson = lesson_selector.by_uuid(validated_data['lesson_uuid'], instructor)
        resource = resource_selector.create(
            validated_data, lesson, instructor
        )
        return resource, lesson
    
    @staticmethod
    def update_text_resource(validated_data: dict, instructor: Instructor) -> CourseLesson:
        lesson = lesson_selector.by_uuid(validated_data['lesson_uuid'], instructor)
        if validated_data.get('notes'):
            lesson.notes = validated_data.get('notes')
        if validated_data.get('related_links') is not None:
            lesson.related_links = validated_data.get('related_links')
        lesson.save()
        return lesson
    
    @staticmethod
    def list_resources(lesson_uuid: str, instructor: Instructor) -> dict:
        lesson = lesson_selector.by_uuid(lesson_uuid, instructor)
        file_resources = resource_selector.by_lesson(lesson, instructor)
        return {
            'lesson_id': lesson.uuid,
            'notes': lesson.notes,
            'related_links': lesson.related_links,
            'file_resources': [
                {
                    'uuid': file_resource.uuid,
                    'title': file_resource.title,
                    'file_name': file_resource.file_name,
                    'file_size': file_resource.file_size,
                    'file_type': file_resource.file_type,
                    'file_key': S3Utils.get_signed_url(file_resource.file_key, expiration=Units.DAY),
                }
                for file_resource in file_resources
            ],
        }
    
    @staticmethod
    def destroy_resource(resource: LessonResource):
        file_key = resource.file_key
        if file_key:
            S3Utils.delete_via_object_key(object_keys=[file_key])
        resource.hard_delete()