from django.urls import path
from rest_framework import routers

from .views import InstructorsViewSet

router = routers.DefaultRouter()
router.register(r'instructors', InstructorsViewSet)

urlpatterns = []

urlpatterns += router.urls