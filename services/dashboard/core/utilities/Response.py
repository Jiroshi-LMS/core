from django.http import JsonResponse, HttpResponse
from rest_framework.status import HTTP_200_OK

class Res():
    """
        Custom Response Class, to send consistently fromatted responses.
    """
    def __init__(self, code=HTTP_200_OK, status=True, data=None, msg=None):
        self.status = status
        self.data = data
        self.msg = msg
        self.code = code

    def json(self):
        resp = {
            'status': self.status,
            'status_code': self.code,
            'response': self.data,
            'msg': self.msg
        }
        return JsonResponse(resp, status=self.code)
    
    def text(self):
        return HttpResponse(self.msg, status=self.code)