import boto3
import structlog
import traceback

from botocore import client
from botocore.exceptions import ClientError
from apps.core.constants import ENV


logger = structlog.get_logger("jiroshi").bind(
    module=__name__
)


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
        except Exception as e:
            logger.error(
                "get_signed_url_failed",
                error=str(e),
                log_type="error",
                extra={'stack': traceback.format_exc()}
            )
            return None

    @staticmethod
    def delete_via_object_key(
            object_keys: list[str],
            bucket_name=ENV.S3_BUCKET,
    ):
        """
        Delete an S3 object using object key.
        """
        try:
            s3_client = boto3.client(
                's3', region_name=ENV.AWS_REGION,
                config=client.Config(signature_version='s3v4'))
            response = s3_client.delete_objects(
                Bucket=bucket_name,
                Delete={
                    "Objects": [{"Key": key} for key in object_keys]
                }
            )
            logger.info("object_keys_deleted", object_keys=object_keys, response=response)
        except Exception as e:
            logger.error(
                "failed_to_delete_object",
                error=str(e),
                log_type="error",
                extra={'stack': traceback.format_exc()}
            )