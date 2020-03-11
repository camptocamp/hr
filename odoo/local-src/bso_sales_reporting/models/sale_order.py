# -*- coding: utf-8 -*-

from odoo import models, api, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    confirmation_date = fields.Datetime(
        track_visibility='onchange',
    )
    order_type = fields.Selection(
        string='Order Type',
        selection=[
            ('create', 'New Project'),
            ('upsell', 'Upsell'),
            ('replace', 'Replacement'),
            ('renew', 'Renewal')
        ],
    )
    nrr = fields.Monetary(
        string='NRR',
        compute='_compute_revenue',
        currency_field='currency_id',
        store=True,
    )
    mrr = fields.Monetary(
        string='MRR',
        compute='_compute_revenue',
        currency_field='currency_id',
        store=True,
    )
    renew_mrr = fields.Monetary(
        string='Renewal MRR',
        compute='_compute_renew_mrr',
        currency_field='currency_id',
        store=True,
    )
    new_mrr = fields.Monetary(
        string='New MRR',
        currency_field='currency_id',
    )
    usd_currency_id = fields.Many2one(
        string='USD Currency',
        comodel_name='res.currency',
        default=lambda self: self.currency_id.browse(3),
        readonly=True,
    )
    rate_usd = fields.Float(
        string='Rate USD',
        compute='_compute_rate_usd',
        store=True,
    )
    nrr_usd = fields.Monetary(
        string='NRR USD',
        compute='_compute_nrr_usd',
        currency_field='usd_currency_id',
        store=True,
    )
    mrr_usd = fields.Monetary(
        string='MRR USD',
        compute='_compute_mrr_usd',
        currency_field='usd_currency_id',
        store=True,
    )
    renew_mrr_usd = fields.Monetary(
        string='Renewal MRR USD',
        compute='_compute_renew_mrr_usd',
        currency_field='usd_currency_id',
        store=True,
    )
    new_mrr_usd = fields.Monetary(
        string='New MRR USD',
        compute='_compute_new_mrr_usd',
        currency_field='usd_currency_id',
        store=True,
    )
    is_delivered = fields.Boolean(
        string='Fully Delivered',
        compute='_compute_delivery_status',
        store=True,
    )
    delivery_date = fields.Date(
        string='Last Delivery Date',
        compute='_compute_delivery_status',
        store=True,
    )
    nrr_is_invoiced = fields.Boolean(
        string='NRR Invoiced',
        compute='_compute_invoice_status',
        store=True,
    )
    nrr_payment_date = fields.Date(
        string='NRR Payment Date',
        compute='_compute_invoice_status',
        store=True,
    )
    mrr_is_invoiced = fields.Boolean(
        string='MRR Invoiced',
        compute='_compute_invoice_status',
        store=True,
    )
    mrr_payment_date = fields.Date(
        string='MRR Payment Date',
        compute='_compute_invoice_status',
        store=True,
    )

    @api.onchange('order_type')
    def onchange_order_type(self):
        if not self.new_mrr:
            self.new_mrr = self.mrr

    @api.depends('order_line.price_subtotal')
    def _compute_revenue(self):
        for rec in self:
            lines = rec.order_line
            lines_nrr = lines.filtered(
                lambda l: not l.product_id.recurring_invoice)
            lines_mrr = lines.filtered(
                lambda l: l.product_id.recurring_invoice)
            rec.update({
                'nrr': sum(lines_nrr.mapped('price_subtotal')),
                'mrr': sum(lines_mrr.mapped('price_subtotal')),
            })

    @api.depends('mrr', 'new_mrr')
    def _compute_renew_mrr(self):
        for rec in self:
            rec.renew_mrr = rec.mrr - rec.new_mrr

    @api.depends('company_id', 'currency_id', 'confirmation_date')
    def _compute_rate_usd(self):
        for rec in self:
            if not all((rec.company_id, rec.currency_id,
                        rec.confirmation_date)):
                continue
            if rec.currency_id.id == rec.usd_currency_id.id:
                rec.rate_usd = 1
            else:
                rec.rate_usd = rec.currency_id.with_context({
                    'company_id': rec.company_id.id,
                    'date': rec.confirmation_date,
                })._get_conversion_rate(rec.currency_id, rec.usd_currency_id)

    @api.depends('nrr', 'rate_usd')
    def _compute_nrr_usd(self):
        for rec in self:
            rec.nrr_usd = rec.nrr * rec.rate_usd

    @api.depends('mrr', 'rate_usd')
    def _compute_mrr_usd(self):
        for rec in self:
            rec.mrr_usd = rec.mrr * rec.rate_usd

    @api.depends('renew_mrr', 'rate_usd')
    def _compute_renew_mrr_usd(self):
        for rec in self:
            rec.renew_mrr_usd = rec.renew_mrr * rec.rate_usd

    @api.depends('new_mrr', 'rate_usd')
    def _compute_new_mrr_usd(self):
        for rec in self:
            rec.new_mrr_usd = rec.new_mrr * rec.rate_usd

    @api.depends(
        'procurement_group_id.procurement_ids.move_ids.picking_id.state',
        'procurement_group_id.procurement_ids.move_ids.picking_id.date_done'
    )
    def _compute_delivery_status(self):
        for rec in self:
            if rec.state not in ('sale', 'done'):
                continue
            procurements = rec.procurement_group_id.procurement_ids
            moves = procurements.mapped('move_ids')
            pickings = moves.mapped('picking_id')
            states = pickings.mapped('state')
            if 'assigned' in states:
                continue
            dates = pickings.mapped('date_done')
            delivery_date = next(iter(sorted(dates, reverse=True)), False)
            rec.update({
                'is_delivered': True,
                'delivery_date': delivery_date,
            })

    @api.depends(
        'partner_id', 'confirmation_date',
        'project_id.invoice_line_ids.invoice_id.state',
        'project_id.invoice_line_ids.invoice_id.date_invoice',
        'project_id.invoice_line_ids.invoice_id.payment_move_line_ids'
    )
    def _compute_invoice_status(self):
        for rec in self:
            if rec.state not in ('sale', 'done'):
                continue
            lines = rec.project_id.invoice_line_ids
            if not lines:
                continue
            order_date = rec.confirmation_date
            if not order_date:
                continue
            lines_out = lines.filtered(
                lambda l:
                l.invoice_id.partner_id.id == rec.partner_id.id
                and l.invoice_id.type == 'out_invoice'
                and l.invoice_id.state in ('open', 'paid')
                and l.invoice_id.date_invoice >= order_date[:10]
            )
            if not lines_out:
                continue
            lines_out_nrr = lines_out.filtered(
                lambda l: not l.product_id.recurring_invoice)
            lines_out_mrr = lines_out.filtered(
                lambda l: l.product_id.recurring_invoice)
            rec.update({
                'nrr_is_invoiced': bool(lines_out_nrr),
                'nrr_payment_date': self._get_payment_date(lines_out_nrr),
                'mrr_is_invoiced': bool(lines_out_mrr),
                'mrr_payment_date': self._get_payment_date(lines_out_mrr),
            })

    def _get_payment_date(self, lines):
        invoice_ids = lines.mapped('invoice_id')
        move_line_ids = invoice_ids.mapped('payment_move_line_ids')
        if not move_line_ids:
            return False
        dates = move_line_ids.mapped('date')
        return sorted(dates)[0]
