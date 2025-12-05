from apps.dashboard.apikeys.constants import KEY_TYPES
from rest_framework.views import APIView
from apps.core.utilities import Res
from apps.core.decorators import handle_exceptions

from .services import InstructorProfileServices
from .permissions import IsValidInstructor


class InstructorProfileView(APIView):
    permission_classes = [IsValidInstructor]
    access_type = KEY_TYPES.get('pk')

    @handle_exceptions
    def get(self, request):
        """
        Fetch instructor and instructor profile details
        by API Key
        """
        instructor = request.instructor
        instructor_profile = InstructorProfileServices.get_instructor_profile(instructor)
        return Res(
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
        ).json()
    