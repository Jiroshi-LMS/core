from .Exceptions import HeadlessException
from ..constants import ERR_CODES



class AuthError(HeadlessException):
    status_code = 401
    default_detail = "Invalid or Expired Token !"
    error_code = ERR_CODES.INVALID_TOKEN_ERR


class InputValidationError(HeadlessException):
    status_code = 400
    default_detail = "Invalid input !"
    error_code = ERR_CODES.VALIDATION_ERR


class NotFoundError(HeadlessException):
    status_code = 404
    default_detail = "Not Found !"
    error_code = ERR_CODES.NOT_FOUND_ERR