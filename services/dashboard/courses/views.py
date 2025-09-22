from core.decorators import handle_exceptions
from core.utilities import Res
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated

from .serializers import CourseSerializer
from .models import Course


class CourseViewSet(ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        """
            Create a new course.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        course = Course.objects.create(
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            thumbnail=serializer.validated_data['thumbnail'],
            duration=serializer.validated_data['duration'],
            created_by=request.user
        )

        return Res(
            status.HTTP_201_CREATED, True, 
            data={
                'course_id': course.uuid,
                'created_by': course.created_by.uuid,
            },
            msg="Course created successfully."
        ).json()

class CourseLessonViewSet(ModelViewSet):
    pass
