from .models import Course, CourseLesson


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