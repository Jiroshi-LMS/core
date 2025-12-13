from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'catalogue', views.CourseCatalogueViewset, basename="course-catalogue")

urlpatterns = [
    path('enroll/', views.CourseEnrollmentView.as_view(), name="enroll-to-course")
]

urlpatterns += router.urls