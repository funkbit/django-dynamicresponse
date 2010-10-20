from django.contrib.auth import authenticate
from django.contrib.auth.models import User, AnonymousUser
from django.conf import settings

class HttpBasicAuthenticationMiddleware:
    """
    Provides automatic user sign-in using HTTP Basic authentication.
    """
    
    def process_request(self, request):
        """"
        Logs in user specified with credentials provided by HTTP authentication.
        """
    
        # Fetch credentials from HTTP request
        auth_string = request.META.get('Authorization', None) or \
            request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_string:
            return False
            
        # Ensure that authentication method is HTTP Basic
        (authmeth, auth) = auth_string.split(" ", 1)
        if not authmeth.lower() == 'basic':
            return False

        # Validate username and password
        auth = auth.strip().decode('base64')
        (username, password) = auth.split(':', 1)
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                request.user = user

        return None
