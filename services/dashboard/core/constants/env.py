from dotenv import load_dotenv
import os

load_dotenv()


class ENV():
    """
        Common Environment Variables
    """
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

    REFRESH_TOKEN_EXP = int(os.getenv('INSTRUCTOR_REFRESH_TOKEN_EXP', 120))