#!/usr/bin/env python
# -*- coding: utf-8 -*-
from inspect import isclass

import inflection
from flask import request
from flask.views import (
    View, http_method_funcs
)

from ._compat import with_metaclass
from .exceptions import (
    ApiNotFound, ApiMethodNotAllowed, ApiNotImplemented
)
from .schema.paged_schema import make_paged_schema


class ResourceMeta(type):
    """Metaclass for :class:``BaseResource`` class."""

    def __new__(mcs, name, bases, attrs):
        klass = type.__new__(mcs, name, bases, attrs)

        if 'methods' not in attrs:
            methods = set(klass.methods or [])
            for attr in attrs:
                if attr in http_method_funcs:
                    methods.add(attr.upper())

            # If we have no method at all in there we don’t want to
            # add a method list. (This is for instance the case for
            # the base class or another subclass of a base method view
            # that does not introduce new methods).
            if methods:
                klass.methods = sorted(methods)

        # Uppercase available methods for convenience.
        klass.methods = [method.upper() for method in klass.methods]
        return klass


class BaseResource(with_metaclass(ResourceMeta, View)):
    """Base class-based view that dispatches request to a particular methods
    and implements the basic CRUD operations for resource::

        class ArtistResource(Resource):
            model = Artist
            schema = ArtistSchema(many=False)
            route = '/artists/<int:artist_id>'

            def get(self, artist_id):
                return self.model.get_by_id(artist_id)

            def put(self, artist_id):
                instance = self.model.get_by_id(artist_id)
                instance, _ = self.schema.load(
                    request.to_json(), instance=instance
                )
                instance.save()
                return instance

    Available options:

    - ``model``: A base class for resource instance. Used as generic
      interface to ORM.
    - ``schema``: A base schema class used to load model instance into the
      view function.
    - ``route``: An URL rule used to register view function.
    - ``many``: A boolean value which indicates that resource should handle a
      collection of objects instead of a single instance.
    - ``methods``: A list of supported methods.

    """
    many = None
    route = None
    model = None
    schema = None

    def dispatch_request(self, *args, **kwargs):
        if request.method not in self.methods:
            raise ApiMethodNotAllowed(
                'API does not support {0!r} method '
                'for requested resource'.format(request.method)
            )

        view_func = getattr(self, request.method.lower(), None)

        # If the request method is HEAD and we don’t have a handler for it
        # retry with GET.
        if view_func is None and request.method == 'HEAD':
            view_func = getattr(self, 'get', None)

        if view_func is None:
            raise ApiNotImplemented

        return view_func(*args, **kwargs)

    def get_instance(self, pk):
        instance = self.model.get_by_id(pk)
        if instance is None:
            raise ApiNotFound
        return instance

    def get(self, pk):
        return self.get_instance(pk)

    def get_many(self):
        paged_schema = make_paged_schema(self.schema)
        return paged_schema.dump(
            self.get_paged_query()
        ).data

    def get_paged_query(self, per_page=20, **kwargs):
        page = 1
        try:
            page = int(request.args.get('page') or 1)
        except (KeyError, ValueError):
            pass

        if page <= 0:
            page = 1

        return self.get_query().paginate(page, per_page, **kwargs)

    def get_query(self):
        return self.model.query

    def post(self):
        instance, _ = self.schema.load(request.get_json())
        instance.save()
        return instance, 201

    def put(self, pk):
        instance, _ = self.schema.load(
            request.get_json(), instance=self.get_instance(pk)
        )
        instance.save()
        return instance, 200

    def delete(self, pk):
        instance = self.get_instance(pk)
        instance.delete()
        return {}, 204

    @classmethod
    def _create_route_from_model(cls):
        """Creates a generic route for model."""
        model_name = cls.model.__name__
        collection_name = inflection.pluralize(cls._resource_name())
        if cls.many:
            return '/{collection_name!s}'.format(
                collection_name=collection_name
            )
        return '/{collection_name!s}/<int:pk>'.format(
            collection_name=collection_name,
            model_name=model_name,
        )

    @classmethod
    def _resource_name(cls):
        """Returns generic resource name, model name by default."""
        return cls.model.__name__

    @classmethod
    def register(cls, api):
        """Helper method for easiest resource registration."""
        api.add_url_rule(
            rule=(cls.route or cls._create_route_from_model()),
            view_func=cls.as_view(cls._resource_name())
        )


class Resource(BaseResource):
    """A generic API resource."""

    many = False
    methods = ()

    @classmethod
    def _resource_name(cls):
        if cls.model:
            return inflection.underscore(cls.model.__name__).lower()


class Collection(BaseResource):
    """A generic API collection."""

    many = True

    @classmethod
    def _resource_name(cls):
        if cls.model:
            return inflection.pluralize(
                inflection.underscore(cls.model.__name__)
            ).lower()

    def get(self):
        return self.get_many()


def register_all_resources(module, api):
    """Convenient helper to register multiple resources."""
    classes = filter(isclass, module.__dict__.values())
    resources = filter(lambda x: issubclass(x, BaseResource), classes)
    for resource in resources:
        if resource is BaseResource or not resource.model:
            continue
        resource.register(api)
