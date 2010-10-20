from django.http import HttpResponse
from dynamicresponse.emitters import JSONEmitter

class JsonResponse(HttpResponse):
    """
    Provides a JSON response to a client, performing automatic serialization.
    """
    
    def __init__(self, object):
        
        # Perform JSON serialization
        emitter = JSONEmitter(object, {}, None)
        content = emitter.render()
        
        # Return response with correct payload/type
        super(JsonResponse, self).__init__(content, mimetype='application/json')
