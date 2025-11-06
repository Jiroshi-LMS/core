from core.decorators import handle_exceptions
from core.utilities import Res
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet


from .serializers import APIKeyBaseSerializer



class APIKeysViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = APIKeyBaseSerializer

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data

        return Res(
            code=status.HTTP_201_CREATED,
            data={},
            msg="API Keys Generated Successfully !"
        ).json()
    
    

