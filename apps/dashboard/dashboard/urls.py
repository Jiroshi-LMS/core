from django.urls import path
from rest_framework import routers

from . import views

# router = routers.DefaultRouter()

urlpatterns = [
    path('kpi/', views.DashboardKPIView.as_view(), name='dashboard-kpi')
]

# urlpatterns += router.urls