from django.utils import timezone
from django.db.models import Q
from apps.dashboard.instructors.models import Instructor
from .models import ApiKeys



class APIKeysSelectors:
    @staticmethod
    def create_key(
        pub_key_hash: str, 
        pvt_key_hash: str,
        validated_data: dict,
        instructor: Instructor
    ):
        """
            API Key creator
        """

        instructor_keys = [
            ApiKeys(
                instructor=instructor, 
                key_name=validated_data.get('key_name'), 
                key_hash=pub_key_hash, 
                key_type='public', 
                expires_at=validated_data.get('expires_at')
            ),
            ApiKeys(
                instructor=instructor, 
                key_name=validated_data.get('key_name'), 
                key_hash=pvt_key_hash, 
                key_type='private', 
                expires_at=validated_data.get('expires_at')
            )
        ]
        keys = ApiKeys.objects.bulk_create(instructor_keys)
        return keys[0].uuid, keys[1].uuid

    @staticmethod
    def get_active_keys(instructor: Instructor):
        """
            List all active API Keys
        """
        return ApiKeys.objects.filter(Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now()), instructor=instructor)
