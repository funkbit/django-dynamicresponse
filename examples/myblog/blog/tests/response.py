import unittest

from mock import Mock
from dynamicresponse.response import *


class DynamicResponseTest (unittest.TestCase):

    def test_serialize_returns_JsonResponse_when_status_is_200(self):
        dynRes = DynamicResponse()
        serialize_result = dynRes.serialize()

        self.assertTrue(isinstance(serialize_result, JsonResponse))
        self.assertTrue(isinstance(serialize_result, HttpResponse))
        self.assertTrue(serialize_result.status_code == 200)

    def test_serialize_returns_HttpResponse_when_status_is_not_200(self):
        dynRes = DynamicResponse(status=CR_DELETED)
        serialize_result = dynRes.serialize()

        self.assertFalse(isinstance(serialize_result, JsonResponse))
        self.assertTrue(isinstance(serialize_result, HttpResponse))
        self.assertTrue(serialize_result.status_code == 204)

        # second example to confirm
        dynRes = DynamicResponse(status=CR_CONFIRM)
        serialize_result = dynRes.serialize()

        self.assertFalse(isinstance(serialize_result, JsonResponse))
        self.assertTrue(isinstance(serialize_result, HttpResponse))
        self.assertTrue(serialize_result.status_code == 405)

    def test_full_context_returns_context_merged_with_extra_context(self):
        testContext = {"testNum": 5, "word": "bird", "beach": 10}
        testExtraContext = {"extra": True, "blue?": False}
        dynResNoExtra = DynamicResponse(testContext)
        dynResWithExtra = DynamicResponse(testContext, extra=testExtraContext)

        for key, value in dynResNoExtra.full_context().items():
            self.assertTrue(testContext[key] == value)

        for key, value in dynResWithExtra.full_context().items():
            self.assertTrue(testContext.get(key) == value or testExtraContext.get(key) == value)


class SerializeOrRenderTest (unittest.TestCase):

    def setUp(self):
        self.sor = SerializeOrRender("invalidtemplate")
        self.sor.serialize = Mock(return_value=HttpResponse())

        self.request = Mock()


    def test_is_instance_of_DynamicResponse(self):
        self.assertTrue(isinstance(self.sor, DynamicResponse))

    def test_render_response_calls_serialize_if_request_is_api_is_true(self):
        self.request.is_api = Mock(return_value=True)

        result = self.sor.render_response(self.request, "unused_variable")

        self.assertTrue(self.sor.serialize.called)
        self.assertTrue(isinstance(result, HttpResponse))

    def test_render_response_calls_django_render_to_response_if_request_is_api_is_false(self):
        self.request.is_api = Mock(return_value=False)

        result = self.sor.render_response(self.request, "unused_variable")

        self.assertTrue(isinstance(result, HttpResponse))

    def test_render_response_attaches_selfs_extra_headers_to_return_element(self):
        self.sor.extra_headers = { 'testh': 1, 'testh2': 2, 'testh3': 3 }
        result = self.sor.render_response(self.request, "unused_variable")

        for header in self.sor.extra_headers:
            self.assertTrue(result.has_header(header))
