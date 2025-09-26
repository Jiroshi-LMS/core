import boto3
import structlog
import traceback

from botocore import client
from botocore.exceptions import ClientError
from core.constants import ENV


logger = structlog.get_logger(__name__)


class S3Utils:

    @staticmethod
    def get_signed_url(
        object_key, 
        bucket_name=ENV.S3_BUCKET, 
        expiration=3600, 
        is_upload=False, 
        content_type: str | None = None
    ):
        """
            Generate a signed URL for fetching a given S3 object.
        """
        try:
            s3_client = boto3.client(
                's3', region_name=ENV.AWS_REGION, 
                config=client.Config(signature_version='s3v4'))
            signed_url_params = {
                'Bucket': bucket_name,
                'Key': object_key,
            }
            if content_type is not None:
                signed_url_params['ContentType'] = content_type
            url = s3_client.generate_presigned_url(
                ClientMethod='put_object' if is_upload else 'get_object',
                Params=signed_url_params,
                ExpiresIn=expiration
            )
            return url
        except ClientError as e:
            logger.error(
                "get_signed_url_failed",
                error=str(e),
                log_type="error",
                extra={'stack': traceback.format_exc()}
            )
            return None