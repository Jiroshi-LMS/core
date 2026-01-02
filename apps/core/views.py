from datetime import datetime
from rest_framework import status
from rest_framework.views import APIView

from .permissions import IsAuthenticated
from .constants import ENV, Keywords
from .decorators import handle_exceptions
from .helpers import get_presigned_object_key
from .utilities import S3Utils
from apps.dashboard.common.utilities.Response import Res


class HealthCheckView(APIView):
    authentication_classes = []
    permission_classes = []
    throttle_classes = []
    
    def get(self, request):
        return Res(msg="Ok").text()


class GetUploadPresignedURL(APIView):
    """
        Get a presigned URL for a given S3 object.
    """
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def post(self, request):
        content_type = request.data.get('content_type')
        prefix = request.data.get('prefix')
        file_name = request.data.get('file_name')
        specific_uuid = request.data.get('specific_id')
        upload_type = request.data.get('upload_type', Keywords.PUBLIC)

        if not prefix or not file_name:
            return Res(
                status.HTTP_400_BAD_REQUEST, False, 
                msg="Missing required fields."
            ).json()
        
        file_name = file_name.replace(' ', '_')
        file_split = file_name.split('.')
        file_name = f"{file_split[0]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
        file_ext = file_split[-1] if len(file_split) > 1 else None
        
        object_key = get_presigned_object_key(
            prefix=prefix,
            file_name=file_name,
            content_type=content_type,
            file_ext=file_ext,
            instructor_uuid=request.user.uuid,
            specific_uuid=specific_uuid
        )

        bucket_name = ENV.S3_BUCKET
        if upload_type == Keywords.PUBLIC:
            bucket_name = ENV.S3_STATIC_BUCKET
        
        url = S3Utils.get_signed_url(
            bucket_name=bucket_name,
            object_key=object_key,
            # content_type=content_type,
            is_upload=True
        )

        return Res(
            status.HTTP_200_OK, True,
            data={
                'upload_url': url,
                'object_key': object_key
            },
            msg="Presigned URL retrieved successfully."
        ).json()
