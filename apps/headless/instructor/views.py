from apps.dashboard.apikeys.constants import KEY_TYPES
from apps.headless.common.permissions.common import IsValidInstructor
from apps.headless.common.utilities.BaseView import HeadlessAPIView
from apps.headless.common.utilities import (ValidationError)
from apps.headless.common.utilities import success

from .services import InstructorProfileServices


class InstructorProfileView(HeadlessAPIView):
    permission_classes = [IsValidInstructor]
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
    