# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.model
    def default_get(self, fields):
        defaults = super(MailComposeMessage, self).default_get(fields)

        if (
                'attachment_ids' in fields and
                self.env.context.get('active_model') == 'sale.order'
        ):
            attachments = self.env['ir.attachment']
            sale_order = self.env['sale.order'].browse(
                self.env.context.get('active_id')
            )
            attachments = sale_order.mapped(
                'attachment_ids'
            )
            defaults['attachment_ids'] = [(6, 0, attachments.ids)]
        return defaults

    @api.multi
    def onchange_template_id(self,
                             template_id,
                             composition_mode,
                             model,
                             res_id):
        values = super(MailComposeMessage, self).onchange_template_id(
            template_id, composition_mode, model, res_id
        )
        value = values['value']
        existing_attachments = self.attachment_ids.ids
        if 'attachment_ids' in value:
            # we want to add attachment, not replace existing attachments
            # so convert (6, 0, ids) to sequences of (4, id, 0)
            for cmd in value['attachment_ids']:
                if cmd[0] == 6:
                    ids = cmd[2]
                    ids += existing_attachments
        return values
