from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
# router.register(r'instructor', views.InstructorViewSet)

urlpatterns = [
    # Student Auth
    path('signup/', views.StudentSignUpView.as_view(), name='student-signup')
]

urlpatterns += router.urls