from django.http import HttpResponse

from dynamicresponse.emitters import JSONEmitter


class JsonResponse(HttpResponse):
    """
    Provides a JSON response to a client, performing automatic serialization.
    """
    
    def __init__(self, object, **kwargs):
        
        # Perform JSON serialization
        emitter = JSONEmitter(object, {}, None)
        content = emitter.render()
        status_code = kwargs.get('status', 200)
        
        # Return response with correct payload/type
        super(JsonResponse, self).__init__(content, mimetype='application/json', status=status_code)
