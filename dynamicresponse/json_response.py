from django.conf import settings
from django.http import HttpResponse

from dynamicresponse.emitters import JSONEmitter

class JsonResponse(HttpResponse):
    """
    Provides a JSON response to a client, performing automatic serialization.
    """
    def __init__(self, object=None, **kwargs):

        # Perform JSON serialization
        if object:
            emitter = JSONEmitter(object, {}, None)
            content = emitter.render()
        else:
            content = ''

        # Status code for the response
        status_code = kwargs.get('status', 200)

        # Return response with correct payload/type
        super(JsonResponse, self).__init__(content, content_type='application/json; charset=%s' % settings.DEFAULT_CHARSET, status=status_code)
