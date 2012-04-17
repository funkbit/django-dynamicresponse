import unittest

from django.http import HttpRequest, HttpResponse, QueryDict
from django.utils.simplejson import loads, dumps
from mock import Mock

from dynamicresponse.middleware.dynamicformat import DynamicFormatMiddleware
from dynamicresponse.response import DynamicResponse


class DynamicFormatTest(unittest.TestCase):

    def setUp(self):
        self.dynamicformat = DynamicFormatMiddleware()
        self.request = HttpRequest()
        self.request._raw_post_data = dumps({
            "testint": 5,
            "teststring": "allihopa",
            "testobj": {
                "anotherint": 10,
                "anotherstring": "bengladesh",
                "testlist": [1, 2, 3, 4, 5]
            },
            "testlist": [1, 2, 3, 4, 5]
        })


    def testFlattenDict(self):
        self.assertTrue(isinstance(self.dynamicformat._flatten_dict(loads(self.request._raw_post_data)), QueryDict))

    def testProcessRequestFlattensPost(self):
        self.dynamicformat._flatten_dict = Mock()
        self.request.META['CONTENT_TYPE'] = 'application/json'
        self.request.META['CONTENT_LENGTH'] = 1

        self.dynamicformat.process_request(self.request)
        self.dynamicformat._flatten_dict.assert_called_once_with(loads(self.request._raw_post_data))

    def testProcessRequestDoesNotFlattenPostIfContentLengthIs0(self):
        self.dynamicformat._flatten_dict = Mock()
        self.request.META['CONTENT_TYPE'] = 'application/json'
        self.request.META['CONTENT_LENGTH'] = 0

        self.dynamicformat.process_request(self.request)
        self.assertFalse(self.dynamicformat._flatten_dict.called, '_flatted_dict was called when it shouldnt have been')

    def testProcessRequestReturnsHttpResponse400WhenPostDataConversionFails(self):
        def raiseException():
            raise

        self.dynamicformat._flatten_dict = Mock(side_effect=raiseException)
        self.request.META['CONTENT_TYPE'] = 'application/json'
        self.request.META['CONTENT_LENGTH'] = 1

        result = self.dynamicformat.process_request(self.request)
        self.assertTrue(isinstance(result, HttpResponse), 'should return instance of HttpResponse')
        self.assertEqual(result.status_code, 400)

    def testProcessResponseCallsRenderResponseOnDynamicResponseObjects(self):
        request = Mock()
        response = HttpResponse()

        self.assertTrue(self.dynamicformat.process_response(request, response) is response,
            'process_response should return the response object if not of instance DynamicResponse')

        response = {}
        self.assertTrue(self.dynamicformat.process_response(request, response) is response,
                        'process_response should return the response object if not of instance DynamicResponse')

        response = DynamicResponse()
        response.render_response = Mock()
        self.dynamicformat.process_response(request, response)
        self.assertTrue(response.render_response.called, 'render_response was not called')
