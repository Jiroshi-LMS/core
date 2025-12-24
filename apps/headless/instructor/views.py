from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.dashboard.dashboard.services import DashboardKPIService
from apps.headless.common.permissions.common import InstructorAPIKeyAuthentication
from apps.headless.common.utilities.BaseView import HeadlessAPIView
from apps.headless.common.utilities import (InputValidationError)
from apps.headless.common.utilities import success

from .services import InstructorProfileServices


class InstructorProfileView(HeadlessAPIView):
    authentication_classes = [InstructorAPIKeyAuthentication]
    access_type = KEY_TYPES.get('pk')

    def get(self, request):
        """
        Fetch instructor and instructor 
        profile details by API Key
        """
        instructor = request.instructor
        instructor_profile = InstructorProfileServices.get_instructor_profile(instructor)
        return success(
            msg="Instructor Profile Fetched !",
            data={
                "instructor": {
                    "username": instructor.username,
                    "email": instructor.email,
                    "country_code": instructor.country_code,
                    "display_name": instructor.full_name,
                    "phone_number": instructor.phone_number
                },
                "profile": instructor_profile
            }
        )
    

class InstructorKPIsView(HeadlessAPIView):
    authentication_classes = [InstructorAPIKeyAuthentication]
    access_type = KEY_TYPES.get('pk')

    def get(self, request):
        """
        Fetch instructor related KPI Data
        """
        kpi_data = DashboardKPIService.get_kpi_data(request.instructor)
        return success(data=kpi_data, msg="KPIs Fetched !")