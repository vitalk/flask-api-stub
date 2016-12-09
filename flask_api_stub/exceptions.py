#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_apify.exc import (
    ApiError, ApiNotImplemented, ApiNotFound
)


class ApiMethodNotAllowed(ApiError):
    code = 405
    description = 'Method not allowed'
