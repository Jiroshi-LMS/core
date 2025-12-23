from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


class StudentTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        refresh = self.token_class

        if "refresh" in data:
            new_refresh = RefreshToken(data["refresh"])

            # 👇 copy custom claims
            for key in ["student_id", "instructor_id"]:
                if key in refresh:
                    new_refresh[key] = refresh[key]

            data["refresh"] = str(new_refresh)

        return data

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