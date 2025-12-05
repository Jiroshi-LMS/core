from .Exceptions import HeadlessException
from ..constants import ERR_CODES


class ValidationError(HeadlessException):
    status_code = 400
    default_detail = "Invalid input !"
    error_code = ERR_CODES.VALIDATION_ERR