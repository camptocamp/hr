# -*- coding: utf-8 -*-
from odoo import http

# class BsoBankStatementAppendButton(http.Controller):
#     @http.route('/bso_update_statement/bso_update_statement/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bso_update_statement/bso_update_statement/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bso_update_statement.listing', {
#             'root': '/bso_update_statement/bso_update_statement',
#             'objects': http.request.env['bso_update_statement.bso_update_statement'].search([]),
#         })

#     @http.route('/bso_update_statement/bso_update_statement/objects/<model("bso_update_statement.bso_update_statement"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bso_update_statement.object', {
#             'object': obj
#         })