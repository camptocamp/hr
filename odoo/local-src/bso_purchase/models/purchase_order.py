# -*- coding: utf-8 -*-
# Copyright 2017-2018 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from odoo import api, models, fields
from datetime import datetime
from dateutil.relativedelta import relativedelta


class Purchase(models.Model):
    _inherit = 'purchase.order'

    subscr_date_start = fields.Date(
        string='Subscription start',
        states={'cancel': [('readonly', True)]},
    )
    subscr_date_end = fields.Date(string='Subscription end')
    subscr_duration = fields.Integer(
        string='Subscription duration (months)',
        states={'cancel': [('readonly', True)]},
        default=12,
    )
    has_subscription = fields.Boolean(
        string='Has subscription',
        compute='_compute_has_subscription',
        readonly=True
    )
    supplier_invoicing_period = fields.Selection(
        [('monthly', u"Monthly"),
         ('quarterly', u"Quarterly"),
         ('yearly', u"Yearly"),
         ],
        string=u"Supplier invoicing period",
        states={'cancel': [('readonly', True)]},
        default='monthly')
    supplier_invoicing_mode = fields.Selection(
        [('end_of_term', u"End of term"),
         ('start_of_term', u"Start of term"),
         ],
        string=u"Supplier invoicing mode",
        states={'cancel': [('readonly', True)]},
        default='end_of_term')
    active = fields.Boolean(
        string=u"Active",
        default=True
    )

    @api.depends('order_line.product_id')
    def _compute_has_subscription(self):
        line_model = self.env['purchase.order.line']
        domain = [('product_id.recurring_invoice', '=', True)]
        for item in self:
            item.has_subscription = bool(line_model.search(
                domain[:] + [('order_id', '=', item.id)]))

    @api.onchange('partner_id', 'company_id')
    def onchange_partner_id(self):
        res = super(Purchase, self).onchange_partner_id()
        field_names = ['supplier_invoicing_period', 'supplier_invoicing_mode']
        values = self.default_get(field_names)
        if self.partner_id:
            values.update(self.partner_id.read(field_names)[0])
            values.pop('id', None)
        self.update(values)
        return res

    @api.onchange('subscr_date_start',
                  'subscr_duration',
                  'has_subscription')
    def onchange_subscr(self):
        if self.has_subscription:
            if self.subscr_date_start and self.subscr_duration:
                self.subscr_date_end = fields.Date.from_string(
                        self.subscr_date_start) + (
                        relativedelta(months=self.subscr_duration))

    @api.model
    def update_qty_received(self, ref_date=None):
        po_lines = self.env['purchase.order.line'].search(
            [('product_id.recurring_invoice', '=', True),
             ('move_ids', '!=', False),
             '|',
             ('order_id.subscr_date_end', '=', False),
             ('order_id.subscr_date_end', '>=',
              ref_date or fields.Date.today()),
             ]
        )
        po_lines._compute_qty_received(ref_date)


class PurchaseLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('order_id.state', 'move_ids.state', 'move_ids.date')
    def _compute_qty_received(self, ref_date=None):
        if ref_date:
            ref_date = fields.Datetime.from_string(ref_date)
        else:
            ref_date = datetime.now()
        UtilsDuration = self.env['utils.duration']
        for line in self:
            qty = 0
            if not line.product_uom.recurring:
                super(PurchaseLine, line)._compute_qty_received()
                continue
            subscr_date_end = fields.Datetime.from_string(
                line.order_id.subscr_date_end)
            # if the ref date is after the end of the purchased subscription
            # we use the end date of the subscription
            calc_date = (min(ref_date, subscr_date_end)
                         if subscr_date_end else ref_date)
            # for each move linked to the current purchase line,
            # add to the current delivered qty:
            # moved qty * (number of months between the move done date
            #              and the calc date)
            moves = self.env['stock.move'].search([
                ('purchase_line_id', '=', line.id),
                ('state', '=', 'done'),
                ('date', '<', fields.Datetime.to_string(calc_date)),
                ]
            )
            for move in moves:
                month_ratio = UtilsDuration.get_month_delta_for_mrc(
                    calc_date, fields.Datetime.from_string(move.date))
                qty += move.product_uom_qty * month_ratio
            line.qty_received = qty
