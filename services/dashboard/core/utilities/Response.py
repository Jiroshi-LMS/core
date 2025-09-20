from core.constants import ENV
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
    
    def json_with_cookies(self, cookie_contents):
        resp = {
            'status': self.status,
            'status_code': self.code,
            'response': self.data,
            'msg': self.msg
        }
        response = JsonResponse(resp, status=self.code)
        response.set_cookie(
            key=cookie_contents['key'],
            value=cookie_contents['value'],
            httponly=True,
            secure=True if ENV.ENVIRONMENT == 'production' else False,
            samesite= 'Strict' if ENV.ENVIRONMENT == 'production' else 'Lax',
            max_age=cookie_contents['expiry_seconds']
        )
        return response
    
    def text(self):
        return HttpResponse(self.msg, status=self.code)