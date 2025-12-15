from .Exceptions import HeadlessException
from ..constants import ERR_CODES



class ServerError(HeadlessException):
    status_code = 500
    default_detail = "Internal Server Error !"
    error_code = ERR_CODES.INTERNAL_ERR


class AuthError(HeadlessException):
    status_code = 401
    default_detail = "Invalid or Expired Token !"
    error_code = ERR_CODES.INVALID_TOKEN_ERR


class ForbiddenError(HeadlessException):
    status_code = 403
    default_detail = "Access denied to this resource !"
    error_code = ERR_CODES.ACCESS_DENIED_ERR


class InputValidationError(HeadlessException):
    status_code = 400
    default_detail = "Invalid input !"
    error_code = ERR_CODES.VALIDATION_ERR


class RecordExistsError(HeadlessException):
    status_code = 400
    default_detail = "Record already exists !"
    error_code = ERR_CODES.ALREADY_EXISTS_ERR


class NotFoundError(HeadlessException):
    status_code = 404
    default_detail = "Not Found !"
    error_code = ERR_CODES.NOT_FOUND_ERR