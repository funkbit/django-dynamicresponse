"""
This file is based on source code from django-piston, available at the following URL:
http://bitbucket.org/jespern/django-piston
"""

from __future__ import generators
from django.db.models.query import QuerySet
from django.db.models import Model, permalink
from django.utils import simplejson
from django.utils.xmlutils import SimplerXMLGenerator
from django.utils.encoding import smart_unicode
from django.core.urlresolvers import reverse, NoReverseMatch
from django.core.serializers.json import DateTimeAwareJSONEncoder
from django.conf import settings
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core import serializers
from django.core.paginator import Page

import decimal, re, inspect
import copy

class Emitter(object):
    """
    Super emitter. All other emitters should subclass
    this one. It has the `construct` method which
    conveniently returns a serialized `dict`. This is
    usually the only method you want to use in your
    emitter. See below for examples.
    """

    EMITTERS = {}
    RESERVED_FIELDS = set([
        'read',
        'update',
        'create',
        'delete',
        'model',
        'anonymous',
        'allowed_methods',
        'fields',
        'exclude'
    ])

    def __init__(self, payload, typemapper, handler, fields=(), anonymous=True):
        
        self.typemapper = typemapper
        self.data = payload
        self.handler = handler
        self.fields = fields
        self.anonymous = anonymous
        
        if isinstance(self.data, Exception):
            raise
    
    def method_fields(self, handler, fields):
        
        if not handler:
            return {}

        ret = dict()
        for field in fields - Emitter.RESERVED_FIELDS:
            t = getattr(handler, str(field), None)

            if t and callable(t):
                ret[field] = t

        return ret
    
    def construct(self):
        """
        Recursively serialize a lot of types, and
        in cases where it doesn't recognize the type,
        it will fall back to Django's `smart_unicode`.
        
        Returns `dict`.
        """

        def _any(thing, fields=()):
            """
            Dispatch, all types are routed through here.
            """
            
            ret = None
            
            if isinstance(thing, QuerySet):
                ret = _qs(thing, fields=fields)
            elif isinstance(thing, Page):
                ret = _list(thing.object_list, fields=fields)
            elif isinstance(thing, (tuple, list)):
                ret = _list(thing, fields=fields)
            elif isinstance(thing, dict):
                ret = _dict(thing, fields=fields)
            elif isinstance(thing, decimal.Decimal):
                ret = str(thing)
            elif isinstance(thing, Model):
                ret = _model(thing, fields=fields)
            elif inspect.isfunction(thing):
                if not inspect.getargspec(thing)[0]:
                    ret = _any(thing())
            elif hasattr(thing, '__emittable__'):
                f = thing.__emittable__
                if inspect.ismethod(f) and len(inspect.getargspec(f)[0]) == 1:
                    ret = _any(f())
            elif repr(thing).startswith("<django.db.models.fields.related.RelatedManager"):
                ret = _any(thing.all())
            else:
                ret = smart_unicode(thing, strings_only=True)

            return ret

        def _fk(data, field):
            """
            Foreign keys.
            """
            
            return _any(getattr(data, field.name))
        
        def _related(data, fields=()):
            """
            Foreign keys.
            """
            
            return [ _model(m, fields) for m in data.iterator() ]
        
        def _m2m(data, field, fields=()):
            """
            Many to many (re-route to `_model`.)
            """
            
            return [ _model(m, fields) for m in getattr(data, field.name).iterator() ]
        
        def _model(data, fields=()):
            """
            Models. Will respect the `fields` and/or
            `exclude` on the handler (see `typemapper`.)
            """
            
            ret = { }
            handler=None
            
            # Does the model implement get_serialization_fields() or serialize_fields()?
            # We should only serialize these fields.
            if hasattr(data, 'get_serialization_fields'):
                fields = set(data.get_serialization_fields())
            if hasattr(data, 'serialize_fields'):
                fields = set(data.serialize_fields())
                    
            # Is the model a user instance?
            # Ensure that only core (non-sensitive fields) are serialized
            if isinstance(data, User):
                fields = ('id', 'email', 'first_name')
                
            # Should we explicitly serialize specific fields?
            if fields:
                
                v = lambda f: getattr(data, f.attname)

                get_fields = set(fields)
                met_fields = self.method_fields(handler, get_fields)
                           
                # Serialize normal fields
                for f in data._meta.local_fields:
                    if f.serialize and not any([ p in met_fields for p in [ f.attname, f.name ]]):
                        if not f.rel:
                            if f.attname in get_fields:
                                ret[f.attname] = _any(v(f))
                                get_fields.remove(f.attname)
                        else:
                            if f.attname[:-3] in get_fields:
                                ret[f.name] = _fk(data, f)
                                get_fields.remove(f.name)
                
                # Serialize many-to-many fields
                for mf in data._meta.many_to_many:
                    if mf.serialize and mf.attname not in met_fields:
                        if mf.attname in get_fields:
                            ret[mf.name] = _m2m(data, mf)
                            get_fields.remove(mf.name)
                
                # Try to get the remainder of fields
                for maybe_field in get_fields:
                    if isinstance(maybe_field, (list, tuple)):
                        model, fields = maybe_field
                        inst = getattr(data, model, None)

                        if inst:
                            if hasattr(inst, 'all'):
                                ret[model] = _related(inst, fields)
                            elif callable(inst):
                                if len(inspect.getargspec(inst)[0]) == 1:
                                    ret[model] = _any(inst(), fields)
                            else:
                                ret[model] = _model(inst, fields)

                    elif maybe_field in met_fields:
                        # Overriding normal field which has a "resource method"
                        # so you can alter the contents of certain fields without
                        # using different names.
                        ret[maybe_field] = _any(met_fields[maybe_field](data))

                    else:    
                        maybe = getattr(data, maybe_field, None)
                        if maybe:
                            if callable(maybe):
                                if len(inspect.getargspec(maybe)[0]) == 1:
                                    ret[maybe_field] = _any(maybe())
                            else:
                                ret[maybe_field] = _any(maybe)
                        else:
                            ret[maybe_field] = _any(maybe)

            else:
                
                for f in data._meta.fields:
                    if not f.attname.startswith('_'):
                        ret[f.attname] = _any(getattr(data, f.attname))

                fields = dir(data.__class__) + ret.keys()
                add_ons = [k for k in dir(data) if k not in fields]

                for k in add_ons:
                    if not k.__str__().startswith('_'):
                        ret[k] = _any(getattr(data, k))

            return ret
        
        def _qs(data, fields=()):
            """
            Querysets.
            """
            
            return [ _any(v, fields) for v in data ]
                
        def _list(data, fields=()):
            """
            Lists.
            """
            
            return [ _any(v, fields) for v in data ]
            
        def _dict(data, fields=()):
            """
            Dictionaries.
            """
            
            return dict([ (k, _any(v, fields)) for k, v in data.iteritems() ])
            
        # Kickstart the seralizin'.
        return _any(self.data, self.fields)
    
    def in_typemapper(self, model, anonymous):
        for klass, (km, is_anon) in self.typemapper.iteritems():
            if model is km and is_anon is anonymous:
                return klass
        
    def render(self):
        """
        This super emitter does not implement `render`,
        this is a job for the specific emitter below.
        """
        raise NotImplementedError("Please implement render.")

class JSONEmitter(Emitter):
    """
    JSON emitter, understands timestamps.
    """

    def render(self):

        indent = 0
        if settings.DEBUG:
            indent = 4
        
        seria = simplejson.dumps(self.construct(), cls=DateTimeAwareJSONEncoder, ensure_ascii=False, indent=indent)
        return seria
