# -*- coding: utf-8 -*-


from odoo.addons.web.controllers.main import ensure_db
from odoo.http import request

from odoo import http


class WebhookController(http.Controller):

    @http.route('/bso_hubspot/webhooks', type='json',
                auth='none', method=['POST'], csrf=False)
    def webhooks(self, **post):
        ensure_db()
        env = request.env
        delayed_lead_model = env['crm.lead'].sudo().with_delay()
        delayed_lead_model.sync(post)
