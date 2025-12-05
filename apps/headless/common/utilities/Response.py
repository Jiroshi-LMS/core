from rest_framework.response import Response
from ..constants import ERR_CODES

def success(data=None, msg="Success", code=200):
    return Response({
        "status": True,
        "results": data != None,
        "message": msg,
        "data": data,
        "error_code": None
    }, status=code)


def error(msg, code=500, error_code=ERR_CODES.INTERNAL_ERR, data=None):
    return Response({
        "status": False,
        "results": data != None,
        "message": msg,
        "data": data,
        "error_code": error_code
    }, status=code)
