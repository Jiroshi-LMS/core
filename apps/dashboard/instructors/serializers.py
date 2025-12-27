from apps.core.constants import DefaultObjectKeys, ENV, Units, Urls
from apps.core.utilities import S3Utils
from rest_framework import serializers
from .models import Instructor, InstructorProfile



class InstructorProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(required=False, allow_null=True, write_only=True)
    location = serializers.CharField(required=False, allow_null=True)
    bio = serializers.CharField(required=False, allow_null=True)
    profile_picture_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = InstructorProfile
        fields = [
            'uuid', 'created_at', 'profile_picture_url',
            'profile_picture', 'location', 'bio'
        ]
        read_only_fields = ['uuid', 'created_at']

    def get_profile_picture_url(self, obj):
        profile_picture = obj.profile_picture
        if not profile_picture: return None
        return Urls.STATIC_S3_URL + profile_picture
    

class InstructorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    country_code = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    profile_completion_status = serializers.CharField(read_only=True)
    profile = InstructorProfileSerializer(read_only=True)
    
    class Meta:
        model = Instructor
        fields = [
            'uuid', 'created_at',
            'full_name', 'username', 'email', 'password', 'country_code', 
            'phone_number', 'profile_completion_status', 'profile'
        ]
        read_only_fields = ['uuid', 'created_at']

    # def get_profile(self, obj):
    #     try:
    #         profile = InstructorProfile.objects.get(instructor=obj)
    #         return InstructorProfileSerializer(profile, read_only=True).data
    #     except InstructorProfile.DoesNotExist:
    #         return None


class InstructorLoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = Instructor
        fields = [
            'email', 'password'
        ]
        read_only_fields = ['email']


class InstructorInfoUpdateSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=False)
    username = serializers.CharField(required=False)
    email = serializers.EmailField(required=False)
    phone_number = serializers.CharField(required=False)
    current_password = serializers.CharField(required=True)

    class Meta:
        model = Instructor
        fields = [
            'uuid', 'created_at', 'full_name', 'username', 'email', 'phone_number',
            'current_password'
        ]
        read_only_fields = ['uuid', 'created_at']