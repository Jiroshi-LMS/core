from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'manager', views.CourseViewSet)
router.register(r'lessons', views.CourseLessonViewSet)

urlpatterns = []

urlpatterns += router.urls