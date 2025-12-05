from .Exceptions import HeadlessException
from ..constants import ERR_CODES


class ValidationError(HeadlessException):
    status_code = 400
    default_detail = "Invalid input !"
    error_code = ERR_CODES.VALIDATION_ERR


class NotFoundError(HeadlessException):
    status_code = 404
    default_detail = "Not Found !"
    error_code = ERR_CODES.NOT_FOUND_ERR