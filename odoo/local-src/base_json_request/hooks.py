# -*- coding: utf-8 -*-
# Copyright 2017 LasLabs Inc.
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import http

from .http import __init__


def post_load():
    """Monkey patch HTTP methods."""
    http.JsonRequest.__init__ = __init__
