from django.urls import path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'catalogue', views.CourseCatalogueViewset, basename="course-catalogue")

urlpatterns = []

urlpatterns += router.urls