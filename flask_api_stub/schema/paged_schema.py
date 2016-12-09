#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import (
    Schema, fields, post_dump
)


class PagingSchema(Schema):
    """Base class for paging schema."""

    page = fields.Int()
    pages = fields.Int()
    per_page = fields.Int()
    total = fields.Int()

    @post_dump(pass_many=False)
    def move_to_meta(self, data):
        items = data.pop('items')
        return {'meta': data, 'items': items}


def make_paged_schema(schema):
    return type(
        '{}Paging'.format(schema.__class__.__name__),
        (PagingSchema,),
        {'items': fields.Nested(schema, many=True)}
    )()
