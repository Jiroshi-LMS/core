from django.urls import path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()
router.register(r'', views.CourseCatalogueViewset, basename="course")


urlpatterns = [
    # Lesson Routes
    path('<uuid:course_uuid>/lessons/', views.CourseLessonViewset.as_view({'get': 'list'}), name="course-lesson-list"),
    path('<uuid:course_uuid>/lessons/<uuid:lesson_uuid>/', views.CourseLessonViewset.as_view({'get': 'retrieve'}), name="course-lesson"),

    # Lesson Resource Routes
    path('<uuid:course_uuid>/lessons/<uuid:lesson_uuid>/resources/', views.LessonResourcesView.as_view(), name="lesson-resources"),

    # Course Enrollment
    path('enroll/', views.CourseEnrollmentView.as_view(), name="enroll-to-course")
]

urlpatterns += router.urls