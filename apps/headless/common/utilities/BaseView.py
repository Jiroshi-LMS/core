from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from .Exceptions import headless_exception_handler

class HeadlessAPIView(APIView):
    def handle_exception(self, exc):
        """
        Override DRF's exception pipeline and force it to use our custom handler.
        """
        response = headless_exception_handler(exc, {"view": self})
        if response is not None:
            return response
        return super().handle_exception(exc)
    
    
class HeadlessModelViewSet(ModelViewSet):
    def handle_exception(self, exc):
        """
        Override DRF's exception handling for ViewSets
        to use the headless error response format.
        """
        response = headless_exception_handler(exc, {"view": self})

        if response is not None:
            return response

        return super().handle_exception(exc)