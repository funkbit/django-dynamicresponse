import unittest

from mock import Mock, patch
from dynamicresponse.response import *


class ResponseTest (unittest.TestCase):

    @patch('dynamicresponse.response.HttpResponse')
    def test_serialize_or_render(self, HttpResponse):
        dynRes = SerializeOrRender('customers/list.html', { 'customers': 'test' })
        self.assertTrue (isinstance(dynRes, DynamicResponse))
