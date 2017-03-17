# -*- coding: utf-8 -*-
# Author: Denis Leemann
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, api


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    @api.multi
    def onchange_template_id(self,
                             template_id,
                             composition_mode,
                             model,
                             res_id):
        values = super(MailComposeMessage, self).onchange_template_id(
            template_id, composition_mode, model, res_id
        )

        if model != 'sale.order':
            return values

        order = self.env['sale.order'].browse(res_id)
        if not order.sales_condition:
            return values

        # xmlids of email.template in which we join the sales condition
        # document
        sale_condition_xmlids = (
            'sale.email_template_edi_sale',
        )
        condition_template_ids = []
        for xmlid in sale_condition_xmlids:
            template = self.env.ref(xmlid, raise_if_not_found=False)
            condition_template_ids.append(template.id)

        # sending a mail quote
        if template_id not in condition_template_ids:
            return values

        attachment = self.env['ir.attachment'].search(
            [('res_model', '=', 'sale.order'),
             ('res_field', '=', 'sales_condition'),
             ('res_id', '=', order.id),
             ],
            limit=1,
        )
        fname = order.sales_condition_filename
        # Replicate what's done in
        # addons/mail_template/wizard/mail_compose_message.py
        # The attachment should be cleaned by odoo later
        data_attach = {
            'name': fname,
            'datas': attachment.datas,
            'datas_fname': fname,
            'res_model': 'mail.compose.message',
            'res_id': 0,
            'type': 'binary',
        }
        new_attachment = self.env['ir.attachment'].create(data_attach)
        value = values['value']
        if 'attachment_ids' in value:
            # add the new attachment to the existing command created
            # by the super onchange
            for cmd in value['attachment_ids']:
                if cmd[0] == 6:
                    ids = cmd[2]
                    ids.append(new_attachment.id)
                else:
                    raise Exception('unhandled')
        else:
            value['attachment_id'] = [(6, 0, new_attachment.ids)]

        return values
