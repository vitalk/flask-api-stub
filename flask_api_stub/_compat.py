#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys

PY2 = sys.version_info[0] == 2

if PY2:
    text_type = unicode
    string_types = basestring,
else:
    text_type = str
    string_types = str,


def with_metaclass(meta, *bases):
    # This requires a bit of explanation: the basic idea is to make a dummy
    # metaclass for one level of class instantiation that replaces itself with
    # the actual metaclass.
    class metaclass(meta):
        def __new__(cls, name, this_bases, d):
            return meta(name, bases, d)
    return type.__new__(metaclass, 'temporary_class', (), {})
