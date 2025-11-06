from core.decorators import handle_exceptions
from core.utilities import Res
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .services import APIKeysServices
from .serializers import APIKeyBaseSerializer



class APIKeysViewset(ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = APIKeyBaseSerializer

    @handle_exceptions
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        pub_key_str, pvt_key_str = APIKeysServices.gen_keys(request.user, validated_data)
        return Res(
            code=status.HTTP_201_CREATED,
            data={
                "public": pub_key_str,
                "private": pvt_key_str
            },
            msg="API Keys Generated Successfully !"
        ).json()
    
    

