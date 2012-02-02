import unittest

from mock import Mock, patch
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
