from rest_framework import serializers
from .models import ApiKeys



class APIKeyBaseSerializer(serializers.ModelSerializer):
    key_name = serializers.CharField(required=True)
    expires_at = serializers.IntegerField(required=True, allow_null=True)

    class Meta:
        model=ApiKeys
        fields = ['key_name', 'expires_at']
