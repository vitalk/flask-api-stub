#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import (
    fields, validates, ValidationError
)


class SurrogateId(object):
    """A mixin that adds a surrogate integer attribute named ``id``
    to any schema class and apply validation to it.
    """

    id = fields.Int()

    @validates('id')
    def instance_should_exists(self, instance_id):
        if self.opts.model:
            instance = self.opts.model.get_by_id(instance_id)
            if not instance:
                raise ValidationError(
                    'Invalid identifier for {!s} instance'.format(
                        self.opts.model.__name__
                    )
                )
