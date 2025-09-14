from rest_framework import viewsets

from .models import Instructor
from .serializers import InstructorSerializer

class InstructorsViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer