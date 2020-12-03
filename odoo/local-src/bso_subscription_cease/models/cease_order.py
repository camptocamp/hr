from odoo import models, fields, api
from datetime import date


class CeaseOrder(models.Model):
    _name = 'cease.order'
    _inherit = ['mail.thread']

    name = fields.Char(
        string='Name'
    )
    submitter = fields.Many2one(
        string='Submiter',
        comodel_name='res.users',
        default=lambda self: self.env.user
    )
    confirmation_date = fields.Date(
        string='Confirmation Date',
        track_visibility='onchange',
    )

    state = fields.Selection(
        [('draft', 'Quotation'),
         ('confirm', 'Confirmed'),
         ('cease', 'Ceased')],
        string='Status',
        default='draft',
        track_visibility='onchange',
    )
    subscription_id = fields.Many2one(
        string='Subscription',
        comodel_name='sale.subscription',
        store=True,
        track_visibility='onchange'
    )
    partner_id = fields.Many2one(
        string='Customer',
        related='subscription_id.partner_id',
        store=True
    )
    customer_contact = fields.Many2one(
        string='Customer contact',
        comodel_name='res.partner',
        domain="[('parent_id', '=', partner_id)]"
    )
    provisioning_contact = fields.Many2one(
        string='Provisioning Contact',
        comodel_name='res.partner',
        domain="[('parent_id', '=', partner_id)]"
    )
    notice_period = fields.Integer(
        string='Notice Period (days)',
    )
    requested_date = fields.Date(
        string='Requested Date'
    )

    project_id = fields.Many2one(
        string='Project',
        related='subscription_id.analytic_account_id',
        store=True
    )
    cease_date = fields.Date(
        string='Cease Date',
        track_visibility='onchange',

    )
    forcast_date = fields.Date(
        string='Forcast Date',
        track_visibility='onchange',
    )
    cease_line_ids = fields.One2many(
        string='Cease Lines',
        comodel_name='cease.order.line',
        inverse_name='cease_id'
    )
    close_reason_id = fields.Many2one(
        string='Reason',
        comodel_name='sale.subscription.close.reason'
    )
    reason_description = fields.Text(
        string='Reason Description'
    )
    notes = fields.Text(
        string='Notes'
    )
    purchase_count = fields.Integer(
        string='Purchase Count',
        compute='compute_purchase_count',
        store=True
    )
    cease_type = fields.Selection(
        [('partial', 'Partial'), ('full', 'Full')],
        string='Cease Type',
        default='partial'
    )
    currency_id = fields.Many2one(
        string='Currency',
        related='subscription_id.currency_id',
        store=True
    )
    usd_currency_id = fields.Many2one(
        string='USD Currency',
        comodel_name='res.currency',
        default=lambda self: self.currency_id.browse(3),
        readonly=True
    )
    loss_mrr = fields.Monetary(
        string='Loss MRR',
        currency_field='currency_id',
        compute='_compute_loss_mrr',
        store=True
    )
    loss_mrr_usd = fields.Monetary(
        string='Loss MRR USD',
        currency_field='currency_id',
        compute='_compute_loss_mrr_usd',
        store=True
    )
    rate_usd = fields.Float(
        string='Rate USD',
        compute='_compute_rate_usd',
        store=True
    )

    @api.depends('currency_id', 'confirmation_date', 'cease_date')
    def _compute_rate_usd(self):
        for rec in self:
            dates = [rec.create_date]
            if rec.confirmation_date:
                dates.append(rec.confirmation_date)
            if rec.cease_date:
                dates.append(rec.cease_date)
            if rec.currency_id.id == rec.usd_currency_id.id:
                rec.rate_usd = 1
            else:
                rec.rate_usd = rec.currency_id.with_context({
                    'company_id': rec.subscription_id.company_id.id,
                    'date': dates[-1],
                })._get_conversion_rate(rec.currency_id, rec.usd_currency_id)

    @api.depends('cease_line_ids', 'close_reason_id')
    def _compute_loss_mrr(self):
        for rec in self:
            if rec.close_reason_id.is_revenue_loss:
                rec.loss_mrr = sum(rec.cease_line_ids.mapped('price_subtotal'))

    @api.depends('loss_mrr', 'rate_usd')
    def _compute_loss_mrr_usd(self):
        for rec in self:
            rec.loss_mrr_usd = rec.loss_mrr * rec.rate_usd

    @api.multi
    def _get_ac_purchase_ids(self):
        return self.env['purchase.order.line'].sudo().search(
            [('account_analytic_id', '=', self.project_id.id)]).mapped(
            'order_id').ids

    @api.multi
    def action_get_purchases(self):
        self.ensure_one()
        purchase_ids = self._get_ac_purchase_ids()
        view_id = self.env.ref('purchase.purchase_order_tree').id
        return {
            'name': 'Purchases',
            'view_type': 'form',
            'view_mode': 'tree',
            'view_id': view_id,
            'domain': [('id', 'in', purchase_ids)],
            'res_model': 'purchase.order',
            'type': 'ir.actions.act_window',
            'target': 'current'}

    @api.depends('subscription_id')
    def compute_purchase_count(self):
        for rec in self:
            rec.purchase_count = len(rec._get_ac_purchase_ids())

    @api.multi
    def action_confirm(self):
        self.ensure_one()
        # create stock.pickings and moves
        # create delivery.project
        return self.write(
            {'state': 'confirm', 'confirmation_date': date.today()})

    @api.multi
    def action_cease(self):
        self.ensure_one()
        self.cease_date = date.today()
        self._update_subscription()
        return self.write({'state': 'cease'})

    @api.multi
    def _update_subscription(self):
        if self.cease_type == 'full':
            self.subscription_id.sudo().write({
                'close_reason_id': self.close_reason_id.id,
                'date_cancelled': self.cease_date,
                'date': self.cease_date
            })
            return self.subscription_id.sudo().set_close()
        else:
            to_remove = [
                (3, line_id) for line_id in self.cease_line_ids.mapped(
                    'subscription_line_id').ids]
            return self.subscription_id.sudo().write(
                {'recurring_invoice_line_ids': to_remove})

    @api.model
    def create(self, vals):
        res = super(CeaseOrder, self).create(vals)
        res.write({'name': '{0}{1:05d}'.format('CO', res.id)})
        return res
