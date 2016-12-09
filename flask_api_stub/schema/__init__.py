#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import (
    post_load,
    Schema as BaseSchema,
    SchemaOpts as BaseSchemaOpts,
)
from flask_apify.exc import ApiUnprocessableEntity
from sqlalchemy_utils.functions import get_primary_keys


class SchemaOpts(BaseSchemaOpts):
    """Options class for base schema class. Adds ``model`` attribute to
    generate instance from.
    """

    def __init__(self, meta):
        super(SchemaOpts, self).__init__(meta)
        self.model = getattr(meta, 'model', None)


class Schema(BaseSchema):
    """Base class for marshmallow schemas."""

    OPTIONS_CLASS = SchemaOpts

    def __init__(self, *args, **kwargs):
        self.instance = kwargs.pop('instance', None)
        super(Schema, self).__init__(*args, **kwargs)

    def handle_error(self, exc, data):
        """Raises API exception when data validation fails."""
        raise ApiUnprocessableEntity(exc.messages)

    @property
    def model_primary_keys(self):
        return get_primary_keys(self.opts.model)

    def get_instance(self, payload):
        """Returns an existing record by they primary keys if any."""
        filters = {
            key: payload.get(key)
            for key in self.model_primary_keys
        }
        if None not in filters.values():
            return self.opts.model.query.filter_by(
                **filters
            ).first()
        return None

    @post_load
    def make_instance(self, payload):
        instance = self.instance or self.get_instance(payload)
        if instance is not None:
            for key, value in payload.items():
                if key not in self.model_primary_keys:
                    setattr(instance, key, value)
            self.instance = None
            return instance
        return self.opts.model(**payload)

    def load(self, data, instance=None, *args, **kwargs):
        """Deserialize data to internal representation."""
        self.instance = instance or self.instance
        return super(Schema, self).load(data, *args, **kwargs)
