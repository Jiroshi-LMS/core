from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'instructor', views.InstructorViewSet)

urlpatterns = [
    path('', views.TestRouteView.as_view(), name='test-route'),
]

urlpatterns += router.urls