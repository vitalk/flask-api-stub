#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask_apify import Apify


class Api(Apify):

    def add_url_rule(self, rule, view_func=None, endpoint=None, **options):
        """Connects a URL rule. Works exactly like the ``route`` decorator but
        support an alternative way to use view functions::

            class CustomerView(View):
                methods = ['GET']

                def dispatch_request(self, name):
                    return 'Hello %s!' % name

            api.add_url_rule('/c/<name>', CustomerView.as_view('customer'))

        """
        if not hasattr(view_func, 'is_api_method'):
            view_func = self.dispatch_api_request(view_func)
            view_func.is_api_method = True

        self.blueprint.add_url_rule(
            rule, view_func=view_func, endpoint=endpoint, **options
        )
