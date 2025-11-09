from .env import ENV

class PresignedPrefix():
    """
        S3 Presigned URL Prefix Constants
    """
    COURSE_THUMBNAIL = "course-thumbnail"
    LESSON_THUMBNAIL = "lesson-thumbnail"
    LESSON_VIDEO = "lesson-video"


class DefaultObjectKeys():
    """
        Default Object Keys
    """
    THUMBNAIL = "defaults/thumbnail-default.jpg"
    PROFILE_PICTURE = "defaults/profile-default.png"

class Urls():
    STATIC_S3_URL = f"https://{ENV.S3_STATIC_BUCKET}.s3.{ENV.AWS_REGION}.amazonaws.com/"
