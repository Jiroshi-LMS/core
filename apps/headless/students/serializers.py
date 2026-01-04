import structlog
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken


logger = structlog.get_logger("jiroshi").bind(
    module=__name__
)


class StudentTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        raw_old_token = attrs.get("refresh")
        old_refresh = RefreshToken(raw_old_token)

        data = super().validate(attrs)
        new_refresh = RefreshToken()

        # copy default claims SimpleJWT expects
        new_refresh = RefreshToken(data["refresh"])

        # copy your custom claims
        for key in ["student_id", "instructor_id"]:
            if key in old_refresh:
                new_refresh[key] = old_refresh[key]

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
    current_password = serializers.CharField(required=True, max_length=72, min_length=8)