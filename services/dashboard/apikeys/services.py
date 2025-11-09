import bcrypt
from django.utils import timezone
from instructors.models import Instructor
from core.helpers import generate_secret

from .constants import MAX_ALLOWED_API_KEYS
from .selectors import APIKeysSelectors

class APIKeysServices:
    @staticmethod
    def gen_keys(instructor: Instructor, validated_data):
        """
            Method to generate pair of public and private
            API Keys for the instructor
        """
        active_key_count = APIKeysSelectors.get_active_keys(instructor).count()
        print(active_key_count)
        if active_key_count >= MAX_ALLOWED_API_KEYS:
            raise ValueError(f"Can't have more than {MAX_ALLOWED_API_KEYS} API Keys active at the same time !")
        pub_key_bytes, pub_key = generate_secret(32)
        pub_key_hash = bcrypt.hashpw(pub_key_bytes, bcrypt.gensalt()).decode()
        pvt_key_bytes, pvt_key = generate_secret(32)
        pvt_key_hash = bcrypt.hashpw(pvt_key_bytes, bcrypt.gensalt()).decode()
        
        expiry_days = validated_data.get('expires_at_days', None)
        if not expiry_days == None:
            expiry_utc = timezone.now() + timezone.timedelta(days=expiry_days) 
            validated_data['expires_at'] = expiry_utc
        pub_uuid, pvt_uuid = APIKeysSelectors.create_key(
            pub_key_hash, 
            pvt_key_hash, 
            validated_data, 
            instructor
        )

        pub_string = f"pk_{pub_uuid}_{pub_key}"
        pvt_string = f"sk_{pvt_uuid}_{pvt_key}"

        return pub_string, pvt_string
        
