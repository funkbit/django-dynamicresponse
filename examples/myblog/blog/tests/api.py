import unittest

from django.http import HttpRequest
from mock import Mock
from dynamicresponse.middleware.api import *


class ApiTest (unittest.TestCase):
    """
    Note: No unit-test for _perform_basic_auth due to the difficulty of mocking django authenticate function.
    """

    def setUp(self):
        self.api = APIMiddleware()
        self.request = HttpRequest()


    def testProcessRequestSetsIsApiFlag(self):
        self.api._detect_api_request = Mock()
        self.api._should_authorize = Mock() # Prevent execution
        self.api._perform_basic_auth = Mock() # Prevent execution
        self.api._require_authentication = Mock() # Prevent execution

        self.api.process_request(self.request)
        self.assertTrue(self.api._detect_api_request.called, '_detect_api_request function was not called, thus is_api is not set')

    def testProcessRequestReturns401IfInvalidRequest(self):
        self.api._detect_api_request = Mock() # Prevent execution
        self.api._should_authorize = Mock(return_value=False)
        self.api._perform_basic_auth = Mock(return_value=False)
        self.api._require_authentication = Mock(return_value='require_auth')

        self.assertTrue(self.api.process_request(self.request) is None)

        self.api._should_authorize = Mock(return_value=True)
        self.assertEqual(self.api.process_request(self.request), 'require_auth')

        self.api._perform_basic_auth = Mock(return_value=True)
        self.assertTrue(self.api.process_request(self.request) is None)

        self.api._should_authorize = Mock(return_value=False)
        self.assertTrue(self.api.process_request(self.request) is None)

    def testProcessResponseReturnsResponseAsIsUnlessItsARedirect(self):
        self.api._require_authentication = Mock(return_value='req_auth')
        self.request.is_api = False
        response = HttpResponse()

        result = self.api.process_response(self.request, response)
        self.assertTrue(result is response, 'process_response should return the same response object')

        self.request.is_api = True
        result = self.api.process_response(self.request, response)
        self.assertTrue(result is response, 'process_response should return the same response object')

        response = HttpResponseRedirect('/invalid/url')
        result = self.api.process_response(self.request, response)
        self.assertTrue(result is response, 'process_response should return the same response object')

        response = HttpResponseRedirect(settings.LOGIN_URL)
        result = self.api.process_response(self.request, response)
        self.assertEqual(result, 'req_auth')

    def testDetectApiRequestSetsApiTrueIfRequestAcceptsJson(self):
        self.request.is_api = False # Keeping pyLint happy
        self.api._detect_api_request(self.request)
        self.assertFalse(self.request.is_api)

        self.request.META['HTTP_ACCEPT'] = 'text/plain'
        self.api._detect_api_request(self.request)
        self.assertFalse(self.request.is_api)

        self.request.META['HTTP_ACCEPT'] = 'application/json'
        self.api._detect_api_request(self.request)
        self.assertTrue(self.request.is_api)

    def testGetAuthStringReturnsStringInAuthenticationHeader(self):
        no_auth = HttpRequest()
        auth1 = HttpRequest()
        auth2 = HttpRequest()

        auth1.META['Authorization'] = 'teststring'
        auth2.META['HTTP_AUTHORIZATION'] = 'teststring'

        self.assertTrue(self.api._get_auth_string(no_auth) is None)
        self.assertEqual(self.api._get_auth_string(auth1), 'teststring')
        self.assertEqual(self.api._get_auth_string(auth2), 'teststring')

    def testShouldAuthorizeReturnsTrueIfRequestNeedsAuthentication(self):
        self.api._get_auth_string = Mock(return_value="blabla")

        self.request.is_api = False
        self.request.user = Mock()
        self.request.user.is_authenticated = Mock(return_value=True)
        self.assertFalse(self.api._should_authorize(self.request))

        self.request.user.is_authenticated = Mock(return_value=False)
        self.assertFalse(self.api._should_authorize(self.request))

        self.request.is_api = True
        self.assertTrue(self.api._should_authorize(self.request))

        self.api._get_auth_string = Mock(return_value=None)
        self.assertFalse(self.api._should_authorize(self.request))

        self.request.user.is_authenticated = Mock(return_value=True)
        self.assertFalse(self.api._should_authorize(self.request))

    def testRequireAuthenticationReturnsValidHttpResponse(self):
        response = self.api._require_authentication()

        self.assertTrue(isinstance(response, HttpResponse), 'Response should be an instance of HttpResponse')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response['WWW-Authenticate'], 'Basic realm="API"')
