from django.urls import path
from rest_framework import routers

from . import views

# router = routers.DefaultRouter()
# router.register(r'views', views.CourseViewSet, basename="courses")
# router.register(r'lessons', views.CourseLessonViewSet)
# router.register(r'resources', views.LessonResourceViewSet)

urlpatterns = [
    # Enrollments
    # path('enrollments/', views.EnrollmentsView.as_view(), name='enrollments-view')
    path('list/', views.StudentListView.as_view(), name="student-list-view")
]

# urlpatterns += router.urls