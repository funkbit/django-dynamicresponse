import unittest

from django.conf import settings
from django.forms import Form
from django.template.base import TemplateDoesNotExist
from django.utils import simplejson
from mock import Mock

from dynamicresponse.response import *

class ConstantTest(unittest.TestCase):

    def test_constants(self):
        self.assertEqual(CR_OK, ('OK', 200))
        self.assertEqual(CR_INVALID_DATA, ('INVALID', 400))
        self.assertEqual(CR_NOT_FOUND, ('NOT_FOUND', 404))
        self.assertEqual(CR_CONFIRM, ('CONFIRM', 405))
        self.assertEqual(CR_DELETED, ('DELETED', 204))
        self.assertEqual(CR_REQUIRES_UPGRADE, ('REQUIRES_UPGRADE', 402))


class DynamicResponseTest(unittest.TestCase):

    def testSerializeReturnsJsonResponseWhenStatusIs200(self):
        dynRes = DynamicResponse()
        serialize_result = dynRes.serialize()

        self.assertTrue(isinstance(serialize_result, JsonResponse), 'Serialized result should be an instance of JsonResponse')
        self.assertTrue(isinstance(serialize_result, HttpResponse), 'Serialized result should be an instance of HttpResponse')
        self.assertEqual(serialize_result.status_code, 200)

    def testSerializeReturnsHttpResponseWhenStatusIs400AndSettingsSpecifyErrorReportingAndNoErrors(self):
        dynRes = DynamicResponse(status=CR_INVALID_DATA)
        settings.DYNAMICRESPONSE_JSON_FORM_ERRORS = True
        serialize_result = dynRes.serialize()

        self.assertTrue(isinstance(serialize_result, HttpResponse), 'Serialized result should be a HttpResponse with correct setting and status: 400')
        self.assertEqual(serialize_result.status_code, 400)

    def testJsonResponseWithStatus400ReturnErrorsWhenSettingsSpecifyErrorReporting(self):
        settings.DYNAMICRESPONSE_JSON_FORM_ERRORS = True
        simple_form = Form()
        simple_form.is_valid = Mock(return_value=False)
        simple_form.errors[u'SimpleError'] = u'This was a very simple error, shame on you'
        simple_form.errors[u'Error2'] = u'This was a bit more serious'

        should_equal = simplejson.dumps({'field_errors': simple_form.errors}, indent=0)

        dynRes = DynamicResponse({}, extra={ 'form': simple_form }, status=CR_INVALID_DATA)
        serialized_result = dynRes.serialize()

        self.assertTrue(isinstance(serialized_result, JsonResponse))
        self.assertEqual(should_equal, serialized_result.content, 'Correct error message is not returned from JsonResponse')

    def testFullContextReturnsContextMergedWithExtraContext(self):
        testContext = {"testNum": 5, "word": "bird", "beach": 10}
        testExtraContext = {"extra": True, "blue?": False}
        dynResNoExtra = DynamicResponse(testContext)
        dynResWithExtra = DynamicResponse(testContext, extra=testExtraContext)

        for key, value in dynResNoExtra.full_context().items():
            self.assertEqual(testContext[key], value)

        for key, value in dynResWithExtra.full_context().items():
            self.assertTrue(testContext.get(key) == value or testExtraContext.get(key) == value,
                            'full_context apperantly did not merge context and extra_context')


class SerializeOrRenderTest(unittest.TestCase):

    def setUp(self):
        self.sor = SerializeOrRender("invalidtemplate")
        self.sor.serialize = Mock(return_value=HttpResponse())

        self.request = Mock()


    def testIsInstanceOfDynamicResponse(self):
        self.assertTrue(isinstance(self.sor, DynamicResponse), 'Should be an instance of DynamicResponse')

    def testRenderResponseCallsSerializeIfRequestIsApiIsTrue(self):
        self.request.is_api = True

        result = self.sor.render_response(self.request, "unused_variable")

        self.assertTrue(self.sor.serialize.called, 'serialize was not called')
        self.assertTrue(isinstance(result, HttpResponse), 'should return an instance of HttpResponse')

    def testRenderResponseCallsDjangoRenderToResponseIfRequestIsApiIsFalse(self):
        self.request.is_api = False
        tried_rendering_template = False

        try:
            self.sor.render_response(self.request, "unused_variable")
        except TemplateDoesNotExist, templatestr:
            self.assertTrue(templatestr.__str__() == "invalidtemplate")
            tried_rendering_template = True

        self.assertTrue(tried_rendering_template, 'render_to_response was not called')

    def testRenderResponseAttachesSelfsExtraHeadersToReturnElement(self):
        self.sor.extra_headers = { 'testh': 1, 'testh2': 2, 'testh3': 3 }
        result = self.sor.render_response(self.request, "unused_variable")

        for header in self.sor.extra_headers:
            self.assertTrue(result.has_header(header), 'apperently did not merge extra_headers with headers')


class SerializeOrRedirectTest(unittest.TestCase):

    def setUp(self):
        self.sor = SerializeOrRedirect("invalidurl")
        self.sor.serialize = Mock(return_value=HttpResponse())

        self.request = Mock()


    def testIsInstanceOfDynamicResponse(self):
        self.assertTrue(isinstance(self.sor, DynamicResponse), 'Should be an instance of DynamicResponse')

    def testRenderResponseCallsSerializeIfRequestIsApiIsTrue(self):
        self.request.is_api = True

        result = self.sor.render_response(self.request, "unused_variable")

        self.assertTrue(self.sor.serialize.called, 'serialize was not called')
        self.assertTrue(isinstance(result, HttpResponse), 'should return an instance of HttpResponse')

    def testRenderResponseReturnsHttpResponseRedirectIfRequestIsApiIsFalse(self):
        self.request.is_api = False

        result = self.sor.render_response(self.request, "unused_variable")

        self.assertTrue(isinstance(result, HttpResponseRedirect), 'should return an instance of HttpResponseRedirect')

    def testRenderResponseAttachesSelfsExtraHeadersToReturnElement(self):
        self.sor.extra_headers = { 'testh': 1, 'testh2': 2, 'testh3': 3 }
        result = self.sor.render_response(self.request, "unused_variable")

        for header in self.sor.extra_headers:
            self.assertTrue(result.has_header(header), 'apperently did not merge extra_headers with headers')


class SerializeTest(unittest.TestCase):

    def setUp(self):
        self.ser = Serialize()
        self.ser.serialize = Mock(return_value=HttpResponse())

        self.request = Mock()


    def testIsInstanceOfDynamicResponse(self):
        self.assertTrue(isinstance(self.ser, DynamicResponse), 'Should be an instance of DynamicResponse')

    def testRenderResponseCallsSerialize(self):
        result = self.ser.render_response(self.request, "unused_variable")

        self.assertTrue(self.ser.serialize.called, 'serialize was not called')
        self.assertTrue(isinstance(result, HttpResponse), 'should return an instance of HttpResponse')

    def testRenderResponseAttachesSelfsExtraHeadersToReturnElement(self):
        self.ser.extra_headers = { 'testh': 1, 'testh2': 2, 'testh3': 3 }
        result = self.ser.render_response(self.request, "unused_variable")

        for header in self.ser.extra_headers:
            self.assertTrue(result.has_header(header), 'extra_headers has apparently not been merged with headers')
