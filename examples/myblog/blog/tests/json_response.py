import unittest
from datetime import datetime

from django.utils import simplejson
from dynamicresponse.json_response import *


class JsonResponseTest (unittest.TestCase):

    def setUp(self):
        self.testObj = { 'testval': 99, 'testStr': 'Ice Cone', 'today': datetime(2012, 5, 17) }
        self.jsonres = JsonResponse(self.testObj)


    def test_is_instance_of_HttpResponse(self):
        self.assertTrue(isinstance(self.jsonres, HttpResponse))

    def test_sets_correct_mimetype(self):
        self.assertTrue(self.jsonres['Content-Type'] == 'application/json')

    def test_converts_content_to_json(self):
        compare_json = simplejson.loads(self.jsonres.content)

        for key, value in compare_json.items():
            self.assertTrue(self.testObj.get(key).__str__() == value.__str__())
