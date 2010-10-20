# django-dynamicresponse

django-dynamicresponse is a lightweight framework for providing REST API's for Django applications.

The framework is intentially very lightweight and minimalistic, and is designed to interoperate with existing Django code, such as form validation, without major changes.

In most cases, the only changes needed to add full REST API to an existing Django application is modifying the return statements in your views to return one of the response classes described below instead of a standard Django `HttpResponse`.

## Features

* Easy integration with existing code
* Decodes submitted JSON into `request.POST`, fully compatible with Django forms
* Built-in support for HTTP Basic authentication

## Installation

* Download and add `django-dynamicresponse` to your `PYTHONPATH`
* Add the two middleware classes to `MIDDLEWARE_CLASSES` in your `settings.py`:

```
MIDDLEWARE_CLASSES = (
    'dynamicresponse.middleware.api.APIMiddleware',
    'dynamicresponse.middleware.dynamicformat.DynamicFormatMiddleware',
)
```

`APIMiddleware` detects incoming API requests based on HTTP headers and provides support for Basic authentication.

`DynamicFormatMiddleware` decodes incoming JSON content into `request.POST`, as well as rendering appropriate responses based on the returned value from your views.

## Usage

Import the dynamicresponse library in the views you want to use it:

```
from dynamicresponse.response import *
```

Return an instance of the appropriate response class depending on your view logic:

```
@login_required
def customer_list(request):
    """Lists all customers."""
    
    customers = Customer.objects.all()
    return SerializeOrRender('customers/list.html', { 'customers': customers })
```

The framework provides two response classes; `SerializeOrRender` and `SerializeOrRedirect`.

As the names imply, these response classes serializes the supplied context as JSON for API requests, and renders a template or redirects to a URL for normal requests. The first argument of both classes specifies the template to be rendered or the URL to redirect the user to.

To implement REST API, you simply use `SerializeOrRender` in situations where you would typically use `render_to_response`, and `SerializeOrRedirect` in cases where you would otherwise return an `HttpResponseRedirect` instance.

For API requests, the second argument of the constructor is the context to be serialized for API requests. When rendering templates, it is often useful to pass additional context (such as forms and paginators) that is only useful when rendering the template, even though they are not relevant for API requests. The `SerializeOrRender` class supports additional context via a third argument, `extra`:

```
@login_required
def customer_list(request):
    """Lists all customers."""
    
    customers = Customer.objects.all()
    return SerializeOrRender('customers/list.html', { 'customers': customers }, extra={ 'somevalue': 'something' })
```

In this case, only `customers` are serialized in API responses, while both `customers` and `somevalue` is accessible when the template is rendered for normal requests.

Content is normally returned as JSON with HTTP status code `200`. If you want to return a different status code, set the `status` argument to one of the following values:

<table>
	<tr>
		<th style="text-align: left">Constant</th>
		<th style="text-align: left">HTTP status</th>
		<th style="text-align: left">Description</th>
	</tr>
	<tr>
		<td>CR_OK</td>
		<td><code>200</code></td>
		<td>Default status</td>
	</tr>
	<tr>
		<td>CR_INVALID_DATA</td>
		<td><code>402</code></td>
		<td>One or more forms are invalid</td>
	</tr>
	<tr>
		<td>CR_NOT_FOUND</td>
		<td><code>404</code></td>
		<td>Not found (optional alternative to <code>HttpResponseNotFound</code> for consistency)</td>
	</tr>
	<tr>
		<td>CR_CONFIRM</td>
		<td><code>405</code></td>
		<td>Confirm action with HTTP POST (use with <code>SerializeOrRender</code> with confirmation template)</td>
	</tr>
	<tr>
		<td>CR_DELETED</td>
		<td><code>204</code></td>
		<td>The resource has been deleted</td>
	</tr>
</table>

You can add custom status values by defining them as a tuple consisting of a string constant and the HTTP status code to return:

```
CR_REQUIRES_UPGRADE = ('REQUIRES_UPGRADE', 402)
```
