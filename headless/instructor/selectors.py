from instructors.models import Instructor, InstructorProfile



class InstructorProfileSelector:
    @staticmethod
    def get_profile(instructor: Instructor):
        return (
            InstructorProfile.objects
            .get(instructor=instructor)
        )