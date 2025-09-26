from dotenv import load_dotenv
import os

load_dotenv()


class ENV():
    """
        Common Environment Variables
    """
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    #JWT
    REFRESH_TOKEN_EXP = int(os.getenv('INSTRUCTOR_REFRESH_TOKEN_EXP', 120))

    #AWS
    S3_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
    S3_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
    AWS_REGION = os.getenv('AWS_REGION')
    S3_BUCKET = os.getenv('AWS_BUCKET_NAME')