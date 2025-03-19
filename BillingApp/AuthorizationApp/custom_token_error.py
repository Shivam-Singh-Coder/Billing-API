from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status

class CustomTokenAuthentication(TokenAuthentication):
    def authenticate(self,request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            raise AuthenticationFailed({
                'isScuss':False,
                'messages': "Your token is invalid or expired. Please try again or refresh token.",
            })
        
def custom_exception_handler(exc,context):
    response = exception_handler(exc,context)
    if isinstance(exc,AuthenticationFailed):
        return Response({
            'isScuss':False,
            'messages': "Your token is invalid or expired. Please try again or refresh token.",
        },
        status=status.HTTP_401_UNAUTHORIZED
        )
    return response