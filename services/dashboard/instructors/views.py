from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Instructor
from .serializers import InstructorSerializer



class TestRouteView(APIView):
    def get(self, request):
        return Response({'message': 'Hello World!'})
    
class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer