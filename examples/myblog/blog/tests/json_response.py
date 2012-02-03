import unittest
from datetime import datetime

from django.utils import simplejson
from dynamicresponse.json_response import *


class JsonResponseTest (unittest.TestCase):

    def setUp(self):
        self.testObj = { 'testval': 99, 'testStr': 'Ice Cone', 'today': datetime(2012, 5, 17) }
        self.jsonres = JsonResponse(self.testObj)


    def testIsInstanceOfHttpResponse(self):
        self.assertTrue(isinstance(self.jsonres, HttpResponse), '')

    def testSetsCorrectMimetype(self):
        self.assertEqual(self.jsonres['Content-Type'], 'application/json')

    def testConvertsContentToJson(self):
        compare_json = simplejson.loads(self.jsonres.content)

        for key, value in compare_json.items():
            self.assertEqual(self.testObj.get(key).__str__(), value.__str__())
