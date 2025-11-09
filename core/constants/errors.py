class CommonErrors():
    INVALID_CREDENTIALS = 'Invalid credentials.'
    INVALID_MOBILE_NUMBER = 'Invalid mobile number.'
    SERVER_ERR = 'Something went wrong. Please try again later.'
    INVALID_USER = 'Invalid user.'
    INVALID_OTP = 'Invalid or Expired OTP.'
    TOKEN_EXPIRED = 'Token expired or invalid.'


class AwsErrorMessages:
    NO_AWS_CREDENTIALS_ERROR = "Unable to authenticate with AWS - please check that valid AWS credentials are configured in settings"
    BUCKET_PERMISSION_CONNECTION_ERROR = "Please verify bucket permissions and network connectivity."
    S3_UPLOAD_FAILED_ERROR = "Failed to upload file to S3 bucket"