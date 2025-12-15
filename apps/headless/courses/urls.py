from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'', views.CourseCatalogueViewset, basename="course")
router.register(r'<str:course_uuid>/lessons', views.CourseLessonViewset, basename="course-lessons")


urlpatterns = [
    path('<uuid:course_uuid>/lessons/', views.CourseLessonViewset.as_view({'get': 'list'})),
    path('<uuid:course_uuid>/lessons/<uuid:lesson_uuid>/', views.CourseLessonViewset.as_view({'get': 'retrieve'})),

    path('enroll/', views.CourseEnrollmentView.as_view(), name="enroll-to-course")
]

urlpatterns += router.urls