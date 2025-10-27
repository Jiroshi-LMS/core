from .models import Course, CourseLesson, LessonResource
from instructors.models import Instructor


class CourseSelector:

    def by_id(self, id, instructor: Instructor, instructor_check=True):
        if instructor_check:
            return Course.objects.get(id=id, created_by=instructor)
        return Course.objects.get(id=id)

    def by_uuid(self, uuid, instructor: Instructor, instructor_check=True):
        if instructor_check:
            return Course.objects.get(uuid=uuid, created_by=instructor)
        return Course.objects.get(uuid=uuid)
    
    def create(self, validated_data, created_by):
        return Course.objects.create(
            title=validated_data.get('title'),
            description=validated_data.get('description'),
            thumbnail=validated_data.get('thumbnail'),
            duration=validated_data.get('duration'),
            created_by=created_by
        )

    def update(self, validated_data, course):
        for key, value in validated_data.items():
            setattr(course, key, value)
        course.save()
        return course


class LessonSelector:

    def by_uuid(self, uuid, instructor: Instructor, instructor_check=True):
        if instructor_check:
            return CourseLesson.objects.get(uuid=uuid, created_by=instructor)
        return CourseLesson.objects.get(uuid=uuid)
    
    def create(self, validated_data, created_by, course):
        return CourseLesson.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            duration=validated_data['duration'],
            created_by=created_by,
            course=course
        )

    def all_lessons(self, course, instructor: Instructor, instructor_check=True):
        if instructor_check:
            return CourseLesson.all_objects.filter(course=course, created_by=instructor)
        return CourseLesson.all_objects.filter(course=course)
    
    def active_lessons(self, course, instructor: Instructor, instructor_check=True):
        if instructor_check:
            return CourseLesson.objects.filter(
                course=course, 
                access_status='active',
                created_by=instructor
            )
        return CourseLesson.objects.filter(
            course=course, 
            access_status='active'
        )
    
    def update(self, validated_data, lesson):
        for key, value in validated_data.items():
            if value is not None:
                setattr(lesson, key, value)
        lesson.save()
        return lesson
    

class LessonResourceSelector():

    def create(self, validated_data, lesson, instructor):
        return LessonResource.objects.create(
            lesson=lesson,
            title = validated_data['title'],
            file_name = validated_data['file_name'],
            file_size = validated_data['file_size'],
            file_type = validated_data['file_type'],
            file_key = validated_data['file_key'],
            created_by = instructor
        )
    
    def by_lesson(self, lesson, instructor: Instructor | None = None, instructor_check=True):
        if instructor_check:
            return LessonResource.objects.filter(lesson=lesson, created_by=instructor)
        return LessonResource.objects.filter(lesson=lesson)