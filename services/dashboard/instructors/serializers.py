from rest_framework import serializers
from .models import Instructor

class InstructorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    country_code = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    profile_completion_status = serializers.CharField(read_only=True)
    profile = serializers.SerializerMethodField()
    
    class Meta:
        model = Instructor
        fields = [
            'uuid', 'created_at',
            'full_name', 'username', 'email', 'password', 'country_code', 
            'phone_number', 'profile_completion_status', 'profile'
        ]
        read_only_fields = ['uuid', 'created_at']

    def get_profile(self, obj):
        return InstructorProfileSerializer(obj, read_only=True).data


class InstructorLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = Instructor
        fields = [
            'username', 'password'
        ]
        read_only_fields = ['username']


class InstructorProfileSerializer(serializers.ModelSerializer):
    profile_picture = serializers.CharField(required=False, default=None)
    location = serializers.CharField(required=False, default=None)
    bio = serializers.CharField(required=False, default="")

    class Meta:
        model = Instructor
        fields = [
            'uuid', 'created_at',
            'profile_picture', 'location', 'bio'
        ]
        read_only_fields = ['uuid', 'created_at']