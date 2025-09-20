from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'instructor', views.InstructorViewSet)

urlpatterns = [
    # Auth
    path('instructor/token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += router.urls