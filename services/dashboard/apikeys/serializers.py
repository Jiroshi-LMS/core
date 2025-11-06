from django.utils import timezone
from rest_framework import serializers
from .models import ApiKeys



class APIKeyBaseSerializer(serializers.ModelSerializer):
    key_name = serializers.CharField(required=True)
    expires_at = serializers.IntegerField(required=True, allow_null=True)

    class Meta:
        model=ApiKeys
        fields = ['key_name', 'expires_at']


class APIKeyListSerializer(serializers.ModelSerializer):
    key_name = serializers.CharField()
    key_type = serializers.CharField()
    status = serializers.SerializerMethodField()
    expires_at = serializers.DateTimeField()

    class Meta:
        model=ApiKeys
        fields = ['uuid', 'key_name', 
                  'key_type', 'status', 
                  'expires_at']

    def get_status(self, obj):
        if not obj.deleted_at == None:
            return 'revoked'
        if obj.expires_at and timezone.now() >= obj.expires_at:
            return 'expired'
        return 'active'
