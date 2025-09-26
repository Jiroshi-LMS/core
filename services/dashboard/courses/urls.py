from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'manager', views.CourseViewSet)
router.register(r'lessons', views.CourseLessonViewSet)

urlpatterns = [
    # File Handling APIs
    path('lessons/get-upload-url/<uuid:lesson_uuid>/', views.GetUploadLessonURL.as_view(), name='get_upload_url')
]

urlpatterns += router.urls