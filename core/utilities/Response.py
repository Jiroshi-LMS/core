from core.constants import ENV
from rest_framework.status import HTTP_200_OK
from rest_framework.response import Response

class Res():
    """
        Custom Response Class, to send consistently fromatted responses.
    """
    def __init__(self, code=HTTP_200_OK, status=True, data=None, msg=None):
        self.status = status
        self.data = data
        self.msg = msg
        self.code = code

    def get_structure(self):
        return {
            'status': self.status,
            'status_code': self.code,
            'response': self.data,
            'msg': self.msg
        }

    def json(self):
        resp = self.get_structure()
        return Response(resp, status=self.code)
    
    def json_with_cookies(self, cookie_contents):
        resp = self.get_structure()
        response = Response(resp, status=self.code)
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
        return Response(self.msg, status=self.code)