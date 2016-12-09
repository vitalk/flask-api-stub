#!/usr/bin/env python
# -*- coding: utf-8 -*-
import inflection
from flask import current_app
from werkzeug.local import LocalProxy
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr


_db = LocalProxy(lambda: current_app.extensions['sqlalchemy'].db)


class SurrogateId(object):
    """A mixin that adds a surrogate integer 'primary key' column named ``id``
    to any declarative-mapped class.
    """
    __table_args__ = {'extend_existing': True}

    id = sa.Column(sa.Integer, primary_key=True)

    @classmethod
    def get_by_id(cls, id):
        if any(
            (isinstance(id, basestring) and id.isdigit(),
             isinstance(id, (int, float))),
        ):
            return cls.query.get(int(id))
        return None


class Model(SurrogateId):
    """Base class for application models."""

    __abstract__ = True
    __table_args__ = {'extend_existing': True}

    @declared_attr
    def __tablename__(cls):
        """Pluralize class name to create a more natural table name."""
        return inflection.tableize(cls.__name__)

    def save(self, commit=True):
        _db.session.add(self)
        if commit:
            _db.session.commit()
        return self

    def update(self, commit=True, **attrs):
        for attr, value in attrs.items():
            setattr(self, attr, value)
        if commit:
            return self.save(commit)
        return self

    def delete(self, commit=True):
        _db.session.delete(self)
        if commit:
            _db.session.commit()

    def __repr__(self):
        values = ', '.join(
            '{0!s}={1!r}'.format(n, getattr(self, n))
            for n in self.__table__.c.keys() if hasattr(self, n)
        )
        return '<{}({})>'.format(self.__class__.__name__, values)
