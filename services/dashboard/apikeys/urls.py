from rest_framework import routers

from .views import APIKeysViewset

router = routers.DefaultRouter()
router.register(r'views', views.APIKeysViewset, basename="apikeys")

urlpatterns = []

urlpatterns += router.urls

