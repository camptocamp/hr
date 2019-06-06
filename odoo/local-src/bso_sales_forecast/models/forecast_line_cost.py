# -*- coding: utf-8 -*-

from odoo import fields, models, api


class ForecastLineCost(models.Model):
    _name = "forecast.line.cost"
    _description = "Forecast Line Cost"

    line_id = fields.Many2one(
        string='Forecast Line',
        comodel_name='forecast.line',
        delegate=True,
        ondelete='cascade',
        required=True,
    )
    purchase_order_line_id = fields.Many2one(
        string='Purchase order Line',
        comodel_name='purchase.order.line',
        readonly=True
    )
    purchase_order_id = fields.Many2one(
        string='Purchase order',
        comodel_name='purchase.order',
        related='purchase_order_line_id.order_id',
        readonly=True
    )
    product_id = fields.Many2one(
        string='Product',
        comodel_name='product.product',
        related='purchase_order_line_id.product_id',
        readonly=True
    )
    categ_id = fields.Many2one(
        string='Category',
        comodel_name='product.category',
        related='product_id.categ_id',
        readonly=True,
    )
    partner_id = fields.Many2one(
        string='Customer',
        comodel_name='res.partner',
        related='purchase_order_id.partner_id',
        readonly=True,
    )
    subs_start_date = fields.Date(
        string='Subscription Start Date',
        related='purchase_order_id.subscr_date_start',
        readonly=True,
    )
    subs_end_date = fields.Date(
        string='Subscription End Date',
        # compute='_compute_subs_end_date',
        # store='True',
    )
    continue_after_end = fields.Boolean(
        string='Continue after end',
        related='purchase_order_id.continue_after_end',
        readonly=True
    )
    form_id = fields.Many2one(
        string='Open',
        comodel_name='forecast.line.cost',
        readonly=True,
    )

    @api.model
    def create(self, values):
        purchase_order_line = self.purchase_order_line_id.browse(
            values['purchase_order_line_id'])
        purchase_order = purchase_order_line.order_id
        report = self.line_id.report_id.browse(values['report_id'])

        subs_start_date = purchase_order.subscr_date_start
        subs_end_dt = self._get_po_end_date(purchase_order, report)
        amount = purchase_order_line.price_subtotal
        values['currency_id'] = purchase_order.currency_id.id
        values['type'] = self.line_id.get_type(purchase_order,
                                               purchase_order_line,
                                               subs_start_date, report,
                                               suffix='c')
        month_amounts = self.line_id.get_month_amounts(subs_start_date,
                                                       subs_end_dt, report,
                                                       amount)
        values.update(month_amounts)
        rec = super(ForecastLineCost, self).create(values)
        rec.form_id = rec.id
        return rec

    @api.model
    def _get_po_end_date(self, purchase_order_id, report_id):
        if purchase_order_id.subscr_date_end \
                and not purchase_order_id.continue_after_end:
            subs_end_date = purchase_order_id.subscr_date_end
        else:
            subs_end_date = report_id.end_date
        return subs_end_date
