from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import BasePermission

class CustomTokenAuthentication(TokenAuthentication):
    def authenticate(self,request):
        try:
            return super().authenticate(request)
        except AuthenticationFailed:
            raise AuthenticationFailed({
                'isSuccess':False,
                'messages': "Your token is invalid or expired. Please try again or refresh token.",
            })
        
def custom_exception_handler(exc,context):
    response = exception_handler(exc,context)
    if isinstance(exc,AuthenticationFailed):
        return Response({
            'isSuccess':False,
            'messages': "Your token is invalid or expired. Please try again or refresh token.",
        },
        status=status.HTTP_401_UNAUTHORIZED
        )
    return response


# class IsAuthenticatedCustom(BasePermission):
#     def has_permission(self, request, view):
#         if not request.user.is_authenticated:
#             return False
#         return True

#     def handle_no_permission(self):
#         return Response({"detail": "You must be logged in to access this resource."}, status=status.HTTP_401_UNAUTHORIZED)





######################## SimpleRateThrottle  ######################
#This is the most common throttling class in DRF. It allows you to define a rate limit based on the number of requests allowed per user/IP within a specified time window.
# 1. Define Throttling Classes in your DRF settings:
# REST_FRAMEWORK = {
#     'DEFAULT_THROTTLE_CLASSES': [
#         'rest_framework.throttling.AnonRateThrottle',
#         'rest_framework.throttling.UserRateThrottle',
#     ],
#     'DEFAULT_THROTTLE_RATES': {
#         'anon': '10/minute',   # 10 requests per minute for anonymous users
#         'user': '1000/day',    # 1000 requests per day for authenticated users
#     },
# }
# 2. Customize Throttling Behavior (Optional):
# from rest_framework.throttling import SimpleRateThrottle

# class CustomRateThrottle(SimpleRateThrottle):
#     scope = 'custom_scope'

#     def get_cache_key(self, request, view):
#         # You can customize how the key is generated based on IP, user, etc.
#         return super().get_cache_key(request, view)

# 3. Apply Throttling to Views:
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework.throttling import UserRateThrottle

# class MyApiView(APIView):
#     throttle_classes = [UserRateThrottle]

#     def get(self, request):
#         return Response({"message": "Hello, world!"})






########################## Custom Throttling Class ##############################
#If you need more complex throttling logic (e.g., based on query parameters, custom limits), you can create a custom throttle class.
# from rest_framework.throttling import BaseThrottle

# class CustomThrottle(BaseThrottle):
#     def allow_request(self, request, view):
#         # Custom logic to allow or reject requests
#         # Return True to allow, False to block
#         return True  # or implement actual rate-limiting logic

#     def wait(self):
#         # How long to wait before the next request is allowed
#         return 60  # in seconds
# from rest_framework.views import APIView
# from rest_framework.response import Response

# class MyApiView(APIView):
#     throttle_classes = [CustomThrottle]

#     def get(self, request):
#         return Response({"message": "Custom throttle"})


########################### Django Ratelimit Middleware ##############################
#You can also use external libraries like django_ratelimit to add more flexible rate-limiting to your views.
# pip install django_ratelimit
# INSTALLED_APPS = [
#     # Other apps...
#     'django_ratelimit',
# ]
# from django_ratelimit.decorators import ratelimit
# from rest_framework.views import APIView
# from rest_framework.response import Response

# @ratelimit(key='ip', rate='5/m', method='ALL', burst=True)
# class MyApiView(APIView):
#     def get(self, request):
#         return Response({"message": "Request successful"})
