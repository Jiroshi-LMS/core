from apps.dashboard.instructors.models import Instructor, InstructorProfile



class InstructorProfileSelector:
    @staticmethod
    def get_profile(instructor: Instructor):
        return (
            InstructorProfile.objects
            .get(instructor_id=1000)
        )