from rest_framework import serializers
from .models import Instructor

class InstructorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(required=True)
    username = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    country_code = serializers.CharField(required=False)
    phone_number = serializers.CharField(required=False)
    
    class Meta:
        model = Instructor
        fields = [
            'id', 'uuid', 'created_at', 'updated_at', 'deleted_at',
            'full_name', 'username', 'email', 'password', 'country_code', 'phone_number'
        ]
        read_only_fields = ['id', 'uuid', 'created_at', 'updated_at', 'deleted_at']


class InstructorLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    class Meta:
        model = Instructor
        fields = [
            'username', 'password'
        ]
        read_only_fields = ['username']