from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse, HttpResponseRedirect

class APIMiddleware:
    """
    Detects API requests and provides support for Basic authentication.
    """
    
    api_accept_types = [
        'application/json',
    ]
    
    def process_request(self, request):
        
        # Check if request is API
        self._detect_api_request(request)
        
        # Should we authenticate based on headers?
        if self._should_authorize(request):
            if not self._perform_basic_auth(request):
                return self._require_authentication()
        
    def process_response(self, request, response):
        
        if not getattr(request, 'is_api', False):
            return response
            
        # Convert redirect from login_required to HTTP 401
        if isinstance(response, HttpResponseRedirect):
            redirect_url = response.get('Location', '')
            if redirect_url.startswith(settings.LOGIN_URL):
                return self._require_authentication()
        
        return response
        
    def _detect_api_request(self, request):
        """
        Detects API request based on the HTTP Accept header.
        If so, sets is_api on the request.
        """
        
        request.is_api = False
        request.accepts = []
        if 'HTTP_ACCEPT' in request.META:
            request.accepts = [a.split(';')[0] for a in request.META['HTTP_ACCEPT'].split(',')]

        for accept_type in request.accepts:
            if accept_type in self.api_accept_types:
                request.is_api = True
    
    def _get_auth_string(self, request):
        """
        Returns the authorization string set in the request header.
        """

        return request.META.get('Authorization', None) or request.META.get('HTTP_AUTHORIZATION', None)
    
    def _should_authorize(self, request):
        """
        Returns true if the request is an unauthenticated API request,
        already containing HTTP authorization headers.
        """
        
        if (not request.is_api) or (request.user.is_authenticated()):
            return False
        else:
            return self._get_auth_string(request) is not None

    def _perform_basic_auth(self, request):
        """"
        Logs in user specified with credentials provided by HTTP authentication.
        """

        # Get credentials from authorization header
        auth_string = self._get_auth_string(request)
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

    def _require_authentication(self):
        """
        Returns a request for authentication.
        """
        
        response = HttpResponse(status=401)
        response['WWW-Authenticate'] = 'Basic realm="%s"' % 'API'
        return response
