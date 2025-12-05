from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
# router.register(r'instructor', views.InstructorViewSet)

urlpatterns = [
    # General Information
    path('profile/', views.InstructorProfileView.as_view(), name='instructor-profile-view')
]

urlpatterns += router.urls