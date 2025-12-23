from rest_framework import serializers


class StudentPasswordAuthRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True, max_length=255)
    password = serializers.CharField(required=True, max_length=72, min_length=8)

class StudentLoginRequestSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=True)
    password = serializers.CharField(required=True, max_length=72)

class StudentDetailsUpdateSerializer(serializers.Serializer):
    identifier = serializers.CharField(required=False, max_length=255)
    password = serializers.CharField(required=False, max_length=72, min_length=8)
    current_password = serializers.CharField(required=True)