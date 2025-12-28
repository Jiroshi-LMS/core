from apps.core.decorators import handle_exceptions
from apps.core.throttles.dashboard_throttle import InstructorRateThrottle
from apps.dashboard.common.utilities.Response import Res
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .services import DashboardKPIService


class DashboardKPIView(APIView):
    """
    KPI views for dashboard
    """
    permission_classes = [IsAuthenticated]
    throttle_classes = [InstructorRateThrottle]
    
    @handle_exceptions
    def get(self, request, *args, **kwargs):
        kpi_data = DashboardKPIService.get_kpi_data(request.user)
        return Res(data=kpi_data, msg="KPIs Fetched !").json()
