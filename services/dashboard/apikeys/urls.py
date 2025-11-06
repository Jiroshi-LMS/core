from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r'views', views.APIKeysViewset, basename="apikeys")

urlpatterns = []

urlpatterns += router.urls

