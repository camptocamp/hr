# -*- coding: utf-8 -*-
import logging

from odoo.http import request

from odoo import http
from utils import _response

_logger = logging.getLogger(__name__)


class BackboneController(http.Controller):
    pop_fields = [
        'code',
        'xco_nrc',
        'address',
        'kva_mrc',
        'currency_id',
        'id',
        'supplier_id',
        'display_name',
        'xco_mrc',
        'bso_name',
        'ixr_name',
        'latitude',
        'x_country_id',
        'rack_nrc',
        'rack_mrc',
        'write_date',
        'supplier_name',
        'active',
        'name',
        'longitude',
        'attachment_number',
        'x_analytic_account_id',
    ]
    device_fields = [
        'supplier_id',
        'display_name',
        'id',
        'bso_name',
        'ixr_name',
        'write_date',
        'supplier_name',
        'active',
        'pop_id',
        'name',
        'attachment_number',
    ]

    @http.route('/api/pops', type='http', auth='none')
    def get_pops(self, active=1, offset=0, limit=None):
        active = 0 if int(active) == 0 else 1
        pops = request.env['backbone.pop'].sudo().search_read([
            ('active', '=', active)
        ], fields=self.pop_fields, offset=int(offset),
            limit=int(limit) if limit else None)
        return _response(pops)

    @http.route('/api/pops/<int:pop_id>', type='http', auth='none')
    def get_pop(self, pop_id):
        pop_model = request.env['backbone.pop']
        pop = pop_model.sudo().search_read([
            ('id', '=', pop_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=self.pop_fields)
        return _response(pop)

    @http.route('/api/devices', type='http', auth='none')
    def get_devices(self, active=1, offset=0, limit=None):
        active = 0 if int(active) == 0 else 1
        devices = request.env['backbone.device'].sudo().search_read([
            ('active', '=', active)
        ], fields=self.device_fields,
            offset=int(offset), limit=int(limit) if limit else None)
        return _response(devices)

    @http.route('/api/devices/<int:device_id>', type='http', auth='none')
    def get_device(self, device_id):
        device_model = request.env['backbone.device']
        device = device_model.sudo().search_read([
            ('id', '=', device_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ], fields=self.device_fields)
        return _response(device)
