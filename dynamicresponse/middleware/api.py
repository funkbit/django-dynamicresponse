from django.contrib.auth import authenticate, login
from django.http import HttpResponse

class APIMiddleware:
    """
    Detects API requests based on request headers, and provides Basic authentication.
    """
    
    api_accept_types = [
        'application/json',
    ]
    
    def process_request(self, request):
        """
        Checks if the request is an API request, and performs authentication.
        """
        
        self._find_request_type(request)
        if not self._perform_basic_auth(request):
        
            # Request authentication if required
            if request.is_api and not request.user.is_authenticated():   
                response = HttpResponse(status=401)
                response['WWW-Authenticate'] = 'Basic realm="%s"' % 'API'
                return response
                    
    def _find_request_type(self, request):
        """
        Sets is_api on the request object to indicate an API request.
        API requests are determined based on the HTTP Accept-header.
        """

        # Split HTTP Accept header
        request.is_api = False
        request.accepts = []
        if 'HTTP_ACCEPT' in request.META:
            request.accepts = [a.split(';')[0] for a in request.META['HTTP_ACCEPT'].split(',')]

        # Is the request an API request?
        for accept_type in request.accepts:
            if accept_type in self.api_accept_types:
                request.is_api = True
    
    def _perform_basic_auth(self, request):
        """"
        Logs in user specified with credentials provided by HTTP authentication.
        """

        # Get credentials from authorization header
        auth_string = request.META.get('Authorization', None) or \
            request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_string:
            return False

        # We only support Basic authentication
        (authmeth, auth) = auth_string.split(" ", 1)
        if not authmeth.lower() == 'basic':
            return False

        # Validate username and password
        auth = auth.strip().decode('base64')
        (username, password) = auth.split(':', 1)
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            request.user = user
            return True
        else:
            return False
