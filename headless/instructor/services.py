from core.constants import Urls
from instructors.models import Instructor, InstructorProfile

from .selectors import InstructorProfileSelector


class InstructorProfileServices:
    @staticmethod
    def get_instructor_profile(instructor: Instructor):
        profile = InstructorProfileSelector.get_profile(instructor)
        profile_picture = None
        if profile.profile_picture:
            profile_picture = Urls.STATIC_S3_URL + profile.profile_picture

        return {
            "bio": profile.bio,
            "location": profile.location,
            "profile_picture": profile_picture
        }
