from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'views', views.CourseViewSet)
router.register(r'lessons', views.CourseLessonViewSet)
router.register(r'resources', views.LessonResourceViewSet)

urlpatterns = []

urlpatterns += router.urls