# -*- coding: utf-8 -*-
# Copyright 2017 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, fields, models


class MrpInvoicing(models.TransientModel):
    _name = 'wizard.mrp.invoicing'
    _description = 'Date for invoicing mrp product'

    ref_date = fields.Datetime(
        required=True,
    )

    @api.multi
    def button_ok(self):
        self.ensure_one()
        sale_order_id = self.env.context.get('active_ids')[0]
        sale_order = self.env['sale.order'].browse(sale_order_id)
        for line in sale_order.order_line:
            line.qty_delivered = line.with_context(
                    ref_date_mrc_delivery=self.ref_date)._get_delivered_qty()
        res = sale_order.get_create_invoice_action()
        # The next wizard need the sale order id in the context
        res['context'] = {
                'active_id': sale_order.id,
                'active_ids': [sale_order.id],
                'ref_date_mrc_delivery': self.ref_date
            }
        if "test_today" in self.env.context:
            # test_today is used by tests to force a date
            # we need to propagate it
            res['context']['test_today'] = self.env.context['test_today']
        return res
