from .models import Course, CourseLesson, LessonResource


class CourseSelector:
    def by_uuid(self, uuid):
        return Course.objects.get(uuid=uuid)
    
    def create(self, validated_data, created_by):
        return Course.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            thumbnail=validated_data['thumbnail'],
            duration=validated_data['duration'],
            created_by=created_by
        )

    def update(self, validated_data, course):
        for key, value in validated_data.items():
            setattr(course, key, value)
        course.save()
        return course


class LessonSelector:

    def by_uuid(self, uuid):
        return CourseLesson.objects.get(uuid=uuid)
    
    def create(self, validated_data, created_by, course):
        return CourseLesson.objects.create(
            title=validated_data['title'],
            description=validated_data['description'],
            duration=validated_data['duration'],
            created_by=created_by,
            course=course
        )

    def all_lessons(self, course):
        return CourseLesson.all_objects.filter(course=course)
    
    def active_lessons(self, course):
        return CourseLesson.objects.filter(
            course=course, 
            access_status='active'
        )
    

class LessonResourceSelector():

    def create(self, validated_data, lesson):
        return LessonResource.objects.create(
            lesson=lesson,
            title = validated_data['title'],
            file_name = validated_data['file_name'],
            file_size = validated_data['file_size'],
            file_type = validated_data['file_type'],
            file_key = validated_data['file_key'],
        )
    
    def by_lesson(self, lesson):
        return LessonResource.objects.filter(lesson=lesson)