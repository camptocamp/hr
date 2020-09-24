# -*- coding: utf-8 -*-
import logging

from odoo.http import request

from odoo import http
from utils import _response

_logger = logging.getLogger(__name__)


class BackboneController(http.Controller):

    @http.route('/api/pops', type='http', auth='none')
    def get_pops(self, active=1, offset=0, limit=None):
        active = 0 if int(active) == 0 else 1
        pops = request.env['backbone.pop'].sudo().search_read([
            ('active', '=', active)
        ], offset=int(offset), limit=int(limit) if limit else None)
        return _response(pops)

    @http.route('/api/pop/<int:pop_id>', type='http', auth='none')
    def get_pop(self, pop_id):
        pop_model = request.env['backbone.pop']
        pop = pop_model.sudo().search_read([
            ('id', '=', pop_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ])
        return _response(pop)

    @http.route('/api/devices', type='http', auth='none')
    def get_devices(self, active=1, offset=0, limit=None):
        active = 0 if int(active) == 0 else 1
        devices = request.env['backbone.device'].sudo().search_read([
            ('active', '=', active)
        ], offset=int(offset), limit=int(limit) if limit else None)
        return _response(devices)

    @http.route('/api/device/<int:device_id>', type='http', auth='none')
    def get_device(self, device_id):
        device_model = request.env['backbone.device']
        device = device_model.sudo().search_read([
            ('id', '=', device_id),
            '|',
            ('active', '=', True),
            ('active', '=', False),
        ])
        return _response(device)
