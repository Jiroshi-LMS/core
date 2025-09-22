from django.db.models import Q

from .models import Instructor, InstructorProfile

class InstructorSelector:
    """
    Selector for instructors.
    """

    def get_by_id(self, instructor_id):
        """
        Get an instructor by ID.
        """
        return Instructor.objects.get(id=instructor_id)

    def get_by_username_or_email(self, username_or_email: str):
        """
        Get an instructor by username or email.
        """
        return Instructor.objects.get(Q(username=username_or_email) | Q(email=username_or_email))

    def create_instructor(self, valid_instructor_data: dict):
        """
        Create an instructor.
        """
        return Instructor.objects.create_user(
            full_name=valid_instructor_data.get('full_name'),
            username=valid_instructor_data.get('username'),
            email=valid_instructor_data.get('email'),
            password=valid_instructor_data.get('password'),
            country_code=valid_instructor_data.get('country_code'),
            phone_number=valid_instructor_data.get('phone_number')
        )
    
    def create_update_profile(self, instructor: Instructor, valid_profile_data: dict):
        """
        Create or update an instructor profile.
        """
        return InstructorProfile.objects.update_or_create(
            instructor=instructor,
            defaults={
                'profile_picture': valid_profile_data.get('profile_picture'),
                'location': valid_profile_data.get('location'),
                'bio': valid_profile_data.get('bio'),
            }
        )