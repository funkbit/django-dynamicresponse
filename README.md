# django-dynamicresponse

django-dynamicresponse is a lightweight framework for easily providing REST API's for Django applications.

The framework is intentionally very lightweight and minimalistic, and is designed to interoperate with existing Django code (such as form validation), without major changes.

In most cases, the only changes needed to add full REST API to an existing Django application is modifying the return statements in your views to return one of the response classes described below instead of a standard Django `HttpResponse`.

## Features

* Easy integration with existing code
* Reuse same views and logic for both API and normal requests (no need for separate API handlers)
* Decodes submitted JSON into `request.POST`, fully compatible with Django forms
* Built-in support for HTTP Basic authentication

## Installation

Install `django-dynamicresponse`:

	pip install django-dynamicresponse

Alternatively, download the source code and manually add it to your `PYTHONPATH`.

Add the two middleware classes to `MIDDLEWARE_CLASSES` in your `settings.py`:
 
	MIDDLEWARE_CLASSES = (
	   'dynamicresponse.middleware.api.APIMiddleware',
	   'dynamicresponse.middleware.dynamicformat.DynamicFormatMiddleware',
	)
	
`APIMiddleware` detects incoming API requests based on HTTP headers and provides support for Basic authentication.

`DynamicFormatMiddleware` decodes incoming JSON content into `request.POST`, as well as rendering appropriate responses based on the returned value from your views.

## Tests

Run unit-tests by running <code>python setup.py test</code>

## Usage

See the included [sample project](http://github.com/funkbit/django-dynamicresponse/tree/master/examples/) for sample code using the framework to implement a simple blog application.

Import `dynamicresponse` in the views you want to use it:

```
from dynamicresponse.response import *
```

Return an instance of the appropriate response class depending on your view logic:

    @login_required
    def customer_list(request):
        """Lists all customers."""
    
        customers = Customer.objects.all()
        return SerializeOrRender('customers/list.html', { 'customers': customers })

The framework provides two response classes; `SerializeOrRender` and `SerializeOrRedirect`.

As the names imply, these response classes serialize the supplied context as JSON for API requests, and renders a template or redirects to a URL for normal requests. The first argument of both classes specifies the template to be rendered or the URL to redirect the user to.

To implement a REST API, you simply use `SerializeOrRender` in situations where you would typically use `render_to_response`, and `SerializeOrRedirect` in cases where you would otherwise return an `HttpResponseRedirect` instance.

For API requests, the second argument of the constructor is the context to be serialized for API requests. When rendering templates, it is often useful to pass additional context (such as forms and paginators) that is only useful when rendering the template, even though they are not relevant for API requests. The `SerializeOrRender` class supports additional context via a third argument, `extra`:

    @login_required
    def customer_list(request):
        """Lists all customers."""
    
        customers = Customer.objects.all()
        return SerializeOrRender('customers/list.html', { 'customers': customers }, extra={ 'somevalue': 'something' })

In this case, only `customers` are serialized in API responses, while both `customers` and `somevalue` is accessible when the template is rendered for normal requests.

### Status codes

Content is normally returned as JSON with HTTP status code `200`. If you want to return a different status code, set the `status` argument to one of the following values:

<table>
    <tr>
        <th align="left">Constant</th>
        <th align="left">HTTP status</th>
        <th align="left">Description</th>
    </tr>
    <tr>
        <td><code>CR_OK</code></td>
        <td><code>200</code></td>
        <td>Default status</td>
    </tr>
    <tr>
        <td><code>CR_INVALID_DATA</code></td>
        <td><code>400</code></td>
        <td>One or more forms are invalid</td>
    </tr>
    <tr>
        <td><code>CR_NOT_FOUND</code></td>
        <td><code>404</code></td>
        <td>Not found (optional alternative to <code>HttpResponseNotFound</code> for consistency)</td>
    </tr>
    <tr>
        <td><code>CR_CONFIRM</code></td>
        <td><code>405</code></td>
        <td>Confirm action with HTTP POST (use with <code>SerializeOrRender</code> with confirmation template)</td>
    </tr>
    <tr>
        <td><code>CR_DELETED</code></td>
        <td><code>204</code></td>
        <td>The resource has been deleted</td>
    </tr>
</table>

You can add custom status values by defining them as a tuple consisting of a string constant and the HTTP status code to return:

	CR_REQUIRES_UPGRADE = ('REQUIRES_UPGRADE', 402)

### Customizing serialization

By default, all fields not starting with an underscore (<code>_</code>) on the models will be serialized when returning a JSON response for API requests.

You can override this behavior by adding a <code>serialize_fields</code> method to your models, returning the fields to include:

	class BlogPost(models.Model):

	    title = models.CharField('Title', max_length=255)
	    text = models.TextField('Text')

	    def serialize_fields(self):
	        """Only these fields will be included in API responses."""
        
	        return [
	            'id',
	            'title',
	            'content',
	        ]

This behavior also extends to nested objects. For instance, if the model above had included a foreign key to an author, only the fields defined in the author's <code>serialize_fields</code> method would have been included.

By default, callables are not included in the serialization. However, you can include names of callables in <code>serialize_fields</code> to explicitly include them in the serialization. This can for instance be useful to provide API users with useful dynamically computed information.
